import cocoindex as coco
from cocoindex.resources.file import PatternFilePathMatcher
from dataclasses import dataclass
from typing import Any, Collection, List
from collections.abc import AsyncIterator
from cocoindex.connectors import localfs, neo4j
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from dataclasses import dataclass
from litellm import acompletion
import pathlib
import litellm
import asyncio
import instructor
import os

load_dotenv()

KG_DB = coco.ContextKey[neo4j.ConnectionFactory]("kg_db")
LLM_MODEL = coco.ContextKey[str]("llm_model", detect_change=True)


@dataclass
class Document:
    filename: str  # primary key
    title: str
    summary: str

@dataclass
class Entity:
    value: str  # primary key — the concept name

@dataclass
class Relationship:
    """RELATIONSHIP edge payload. ``id`` is a stable hash of the triple so the
    same (subject, predicate, object) always maps to a single edge; the
    ``predicate`` is stored as an edge property."""
    id: int
    predicate: str
    
@dataclass
class Triple:
    subject: str
    predicate: str
    object: str


@dataclass
class DocTriples:
    filename: str
    triples: list[Triple]



class DocumentSummary(BaseModel):
    title: str = Field(description="A concise title for the document.")
    summary: str = Field(
        description="A one-paragraph summary of what the document covers."
    )
    
class ExtractedRelationship(BaseModel):
    subject:str
    predicate:str
    object:str
    
class RelationshipList(BaseModel):
    relationships: List[ExtractedRelationship]
    
    
SUMMARY_PROMPT = """
    You are a document summarization assistant.

    Given the content of a document:
    1. Generate a concise, descriptive title.
    2. Write a one-paragraph summary explaining what the document is about.
    3. Base the title and summary only on information present in the document.

    Return the result using the provided structured output schema.
"""
    
    
RELATIONSHIP_PROMPT = """
    You are a knowledge graph extraction assistant.

    Extract the important entities and relationships from the document.

    For each relationship, identify:
    - subject: the entity performing or owning the relationship
    - predicate: the relationship between the entities
    - object: the entity being related to

    Only extract relationships that are explicitly stated or strongly supported by the document.
    Do not invent entities or relationships.

    Examples:

    Python is used for machine learning.

    → subject: Python
    → predicate: used_for
    → object: machine learning

    Google acquired YouTube in 2006.

    → subject: Google
    → predicate: acquired
    → object: YouTube

    Return all extracted relationships using the provided structured output schema.
"""


@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    builder.provide(
        KG_DB,
        neo4j.ConnectionFactory(
            uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            auth=(
                os.environ.get("NEO4J_USER", "neo4j"),
                os.environ.get("GRAPH_DB_PASSWORD", "password@1234"),
            ),
            database=os.environ.get("NEO4J_DATABASE", "neo4j"),
        ),
    )
    builder.provide(LLM_MODEL, os.environ.get("LLM_MODEL", "openai/gpt-5-mini"))
    yield
    
    
@coco.fn(memo=True)
async def extract_relationships(content: str) -> list[Triple]:
    client = instructor.from_litellm(litellm.acompletion, mode=instructor.Mode.JSON)
    result = await client.chat.completions.create(
        model=coco.use_context(LLM_MODEL),
        response_model=RelationshipList,
        messages=[
            {"role": "system", "content": RELATIONSHIP_PROMPT},
            {"role": "user", "content": content},
        ],
    )
    validated = RelationshipList.model_validate(result.model_dump())
    return [Triple(r.subject, r.predicate, r.object) for r in validated.relationships]

@coco.fn(memo=True)
async def extract_summary(content: str) -> DocumentSummary:
    client = instructor.from_litellm(litellm.acompletion, mode=instructor.Mode.JSON)
    result = await client.chat.completions.create(
        model=coco.use_context(LLM_MODEL),
        response_model=DocumentSummary,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": content},
        ],
    )
    return DocumentSummary.model_validate(result.model_dump())

@coco.fn(memo=True)
async def process_file(
    file: localfs.File,
    document_table: neo4j.TableTarget[Document],
) -> DocTriples:
    content = await file.read_text()
    filename = file.file_path.path.as_posix()

    summary = await extract_summary(content)
    document_table.declare_record(
        row=Document(filename=filename, title=summary.title, summary=summary.summary)
    )

    triples = await extract_relationships(content)
    return DocTriples(filename=filename, triples=triples)


@coco.fn
async def build_graph(
    docs: list[DocTriples],
    entity_table: neo4j.TableTarget[Entity],
    relationship_rel: neo4j.RelationTarget[Relationship],
    mention_rel: neo4j.RelationTarget[Any],
) -> None:
    entities: set[str] = set()
    mentions: set[tuple[str, str]] = set()  # (filename, entity value)

    for doc in docs:
        for t in doc.triples:
            entities.add(t.subject)
            entities.add(t.object)
            mentions.add((doc.filename, t.subject))
            mentions.add((doc.filename, t.object))

            rel_id = await generate_id((t.subject, t.predicate, t.object))
            relationship_rel.declare_relation(
                from_id=t.subject,
                to_id=t.object,
                record=Relationship(id=rel_id, predicate=t.predicate),
            )

    for value in entities:
        entity_table.declare_record(row=Entity(value=value))

    for filename, entity in mentions:
        mention_rel.declare_relation(from_id=filename, to_id=entity)
        
        
        
@coco.fn
async def app_main(sourcedir: pathlib.Path) -> None:
    document_table = await neo4j.mount_table_target(
        KG_DB,
        "Document",
        await neo4j.TableSchema.from_class(Document, primary_key="filename"),
        primary_key="filename",
    )
    entity_table = await neo4j.mount_table_target(
        KG_DB,
        "Entity",
        await neo4j.TableSchema.from_class(Entity, primary_key="value"),
        primary_key="value",
    )
    relationship_rel = await neo4j.mount_relation_target(
        KG_DB,
        "RELATIONSHIP",
        entity_table,
        entity_table,
        await neo4j.TableSchema.from_class(Relationship, primary_key="id"),
        primary_key="id",
    )
    mention_rel = await neo4j.mount_relation_target(
        KG_DB, "MENTION", document_table, entity_table
    )

    files = localfs.walk_dir(
        sourcedir,
        recursive=True,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.md", "**/*.mdx"]),
    )
    file_coros = []
    async for path_key, file in files.items():
        file_coros.append(
            coco.use_mount(
                coco.component_subpath("file", path_key),
                process_file,
                file,
                document_table,
            )
        )
    docs: list[DocTriples] = list(await asyncio.gather(*file_coros))

    await coco.mount(
        coco.component_subpath("build_graph"),
        build_graph,
        docs,
        entity_table,
        relationship_rel,
        mention_rel,
    )


app = coco.App(
    coco.AppConfig(name="DocsToKnowledgeGraph"),
    app_main,
    sourcedir=pathlib.Path("./ats"),
)


if __name__ == "__main__":
    print(app)