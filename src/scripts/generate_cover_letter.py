"""
Generate Customized Cover Letter PDF

Reads template markdown from Resumes/cover_letter.md, injects the specified
company_name and job_role, and exports a professionally formatted PDF to
Resumes/cover_letter/cover_letter_<company>.pdf using markdown-pdf.

Usage:
    Command line:
        python src/scripts/generate_cover_letter.py "Google" "AI/ML Engineer"
        python src/scripts/generate_cover_letter.py --company "Anthropic" --role "Research Engineer"

    In Python:
        from src.scripts.generate_cover_letter import generate_cover_letter
        pdf_path = generate_cover_letter(company_name="Google", job_role="AI Engineer")
"""

import os
import re
import sys
import argparse
from pathlib import Path
from markdown_pdf import MarkdownPdf, Section

# Default workspace root (D:\Projects\PRACTICE\firecrawl_test)
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_TEMPLATE = WORKSPACE_ROOT / "Resumes" / "cover_letter.md"
DEFAULT_OUTPUT_DIR = WORKSPACE_ROOT / "Resumes" / "cover_letter"

# Professional executive typography stylesheet for the PDF
COVER_LETTER_CSS = """
body {
    font-family: 'Segoe UI', Arial, 'Helvetica Neue', sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1e293b;
    margin: 0;
    padding: 0;
}

h1, h2, h3 {
    color: #0f172a;
    font-weight: 700;
}

h2 {
    font-size: 17pt;
    margin-top: 0;
    margin-bottom: 14px;
    padding-bottom: 6px;
    border-bottom: 2px solid #0284c7;
    letter-spacing: -0.02em;
}

p {
    margin-top: 0;
    margin-bottom: 11px;
    text-align: justify;
}

strong {
    color: #0f172a;
    font-weight: 600;
}

a {
    color: #0284c7;
    text-decoration: none;
}
"""


def sanitize_filename(name: str) -> str:
    """Sanitize company name for clean filesystem paths."""
    # Remove leading/trailing whitespace, replace spaces/punctuations with underscores
    clean = re.sub(r"[^\w\s-]", "", name.strip())
    clean = re.sub(r"[-\s]+", "_", clean)
    return clean or "company"


def customize_cover_letter_markdown(md_text: str, company_name: str, job_role: str) -> str:
    """
    Substitutes company_name and job_role into the markdown text template.
    Handles placeholders as well as natural language phrasing in the template.
    """
    text = md_text

    # 1. Replace explicit template placeholders if present
    text = re.sub(r"\[Company\]|\{company\}|\{company_name\}", company_name, text, flags=re.IGNORECASE)
    text = re.sub(r"\[Role\]|\{job_role\}|\{role\}", job_role, text, flags=re.IGNORECASE)

    # 2. Tailor Salutation: "Dear Hiring Team," -> "Dear {company_name} Hiring Team,"
    text = re.sub(
        r"Dear\s+Hiring\s+Team,",
        f"Dear {company_name} Hiring Team,",
        text,
        count=1
    )

    # 3. Tailor Position & Company opening statement
    # Matches: "I am excited to apply for the **Software Engineer, Machine Learning / AI Engineer** position."
    opening_pattern = r"(I am excited to apply for the\s+)\*\*.*?\*\*(\s+position\.?)"
    if re.search(opening_pattern, text):
        text = re.sub(
            opening_pattern,
            rf"\1**{job_role}** position at **{company_name}**.",
            text,
            count=1
        )
    else:
        # Fallback if pattern was modified
        text = re.sub(
            r"(I am excited to apply for the\s+)(.*?)(\s+position)",
            rf"\1**{job_role}** position at **{company_name}**",
            text,
            count=1
        )

    # 4. Tailor Closing sentence
    # Matches: "contribute to your team." -> "contribute to your team at {company_name}."
    text = re.sub(
        r"could contribute to your team\.",
        f"could contribute to your team at {company_name}.",
        text,
        count=1
    )

    return text


def generate_cover_letter(
    company_name: str,
    job_role: str,
    template_path: str | Path | None = None,
    output_dir: str | Path | None = None
) -> str:
    """
    Generates a customized cover letter PDF for the given company_name and job_role.

    Args:
        company_name: Target company name (e.g. "Google", "Anthropic").
        job_role: Target job position (e.g. "AI Engineer", "Machine Learning Engineer").
        template_path: Path to markdown template (defaults to Resumes/cover_letter.md).
        output_dir: Output directory (defaults to Resumes/cover_letter).

    Returns:
        The absolute path to the generated PDF file ("cover_letter_<company>.pdf").
    """
    if not company_name or not company_name.strip():
        raise ValueError("company_name must not be empty.")
    if not job_role or not job_role.strip():
        raise ValueError("job_role must not be empty.")

    template_file = Path(template_path) if template_path else DEFAULT_TEMPLATE
    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR

    if not template_file.exists():
        raise FileNotFoundError(f"Template not found at: {template_file}")

    # Ensure output directory exists
    out_dir.mkdir(parents=True, exist_ok=True)

    # Read markdown template
    with open(template_file, "r", encoding="utf-8") as f:
        raw_markdown = f.read()

    # Inject company and role
    custom_markdown = customize_cover_letter_markdown(
        raw_markdown,
        company_name=company_name.strip(),
        job_role=job_role.strip()
    )

    # Output file name: cover_letter_<company>.pdf
    slug = sanitize_filename(company_name)
    output_filename = f"cover_letter_{slug}.pdf"
    output_path = out_dir / output_filename

    # Build PDF with markdown-pdf
    pdf = MarkdownPdf(toc_level=0)
    # Margins: 36pt (0.5 in) left/top, -36pt right/bottom
    section = Section(custom_markdown, toc=False, paper_size="A4", borders=(36, 36, -36, -36))
    pdf.add_section(section, user_css=COVER_LETTER_CSS)

    try:
        pdf.save(str(output_path))
    except PermissionError:
        # File is locked by an external PDF viewer (common on Windows); fallback to versioned filename
        for attempt in range(1, 10):
            fallback_filename = f"cover_letter_{slug}_{attempt}.pdf"
            fallback_path = out_dir / fallback_filename
            try:
                pdf.save(str(fallback_path))
                output_path = fallback_path
                break
            except PermissionError:
                continue
        else:
            raise PermissionError(f"Could not write PDF to {output_path} (file locked by an external application).")

    print(f"[SUCCESS] Cover letter generated at: {output_path}")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a customized cover letter PDF from Resumes/cover_letter.md"
    )
    parser.add_argument("company_pos", nargs="?", help="Company name (positional)")
    parser.add_argument("role_pos", nargs="?", help="Job role (positional)")
    parser.add_argument("--company", "-c", dest="company_opt", help="Target company name")
    parser.add_argument("--role", "-r", dest="role_opt", help="Target job role")
    parser.add_argument("--template", "-t", help="Path to markdown template", default=None)
    parser.add_argument("--outdir", "-o", help="Output directory", default=None)

    args = parser.parse_args()

    company = args.company_opt or args.company_pos
    role = args.role_opt or args.role_pos

    if not company:
        company = input("Enter Company Name: ").strip()
    if not role:
        role = input("Enter Job Role: ").strip()

    try:
        pdf_path = generate_cover_letter(
            company_name=company,
            job_role=role,
            template_path=args.template,
            output_dir=args.outdir
        )
        print(f"Result: {pdf_path}")
    except Exception as e:
        print(f"[ERROR] Failed to generate cover letter: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
