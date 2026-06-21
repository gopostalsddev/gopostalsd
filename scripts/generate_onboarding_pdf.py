"""Generate GoPostal SD developer onboarding PDF."""

from fpdf import FPDF
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "GoPostalSD-Developer-Onboarding.pdf"


class OnboardingPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "GoPostal SD - Developer Onboarding", align="R", new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title: str):
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 64, 120)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 64, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def subheading(self, text: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def link_line(self, label: str, url: str):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(30, 30, 30)
        self.cell(38, 6, label)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 102, 204)
        self.cell(0, 6, url, link=url, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def code_block(self, lines: list[str]):
        self.set_fill_color(245, 247, 250)
        self.set_font("Courier", "", 9)
        self.set_text_color(40, 40, 40)
        line_height = 5
        block_height = len(lines) * line_height + 6
        if self.get_y() + block_height > 270:
            self.add_page()
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 190, block_height, style="F")
        self.set_xy(x + 4, y + 3)
        for line in lines:
            self.cell(0, line_height, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(x + 4)
        self.ln(4)

    def bullet(self, text: str, indent: int = 10):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.set_x(indent)
        self.multi_cell(0, 5.5, f"- {text}")
        self.ln(1)

    def env_var(self, name: str, value: str, indent: int = 15):
        self.set_x(indent)
        self.set_font("Courier", "", 9)
        self.set_text_color(80, 80, 80)
        self.cell(52, 5.5, name)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        self.cell(0, 5.5, value, new_x="LMARGIN", new_y="NEXT")


def build_pdf():
    pdf = OnboardingPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(30, 64, 120)
    pdf.cell(0, 12, "GoPostal SD", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "Developer Onboarding", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    pdf.link_line("GitHub:", "https://github.com/gopostalsddev/gopostalsd")
    pdf.link_line(
        "Software Design:",
        "https://github.com/gopostalsddev/gopostalsd/tree/main/docs",
    )
    pdf.body("Prerequisites: Python 3.12+, Node.js 18+, PostgreSQL")

    pdf.section_title("Setup")
    pdf.subheading("1. Clone the repo and create env files (never commit these)")
    pdf.bullet("backend/.env  - copy from backend/env.example")
    pdf.bullet("frontend/.env - see Credentials section below")
    pdf.ln(2)

    pdf.subheading("2. Backend")
    pdf.code_block([
        "cd backend",
        "python -m venv venv",
        "venv\\Scripts\\activate          # Windows",
        "pip install -r requirements.txt",
        "set FLASK_APP=app.py",
        "flask db upgrade",
        "python utility_scripts/setup_database.py",
        "python utility_scripts/create_simple_admin.py",
        "python app.py",
    ])
    pdf.body("API: http://localhost:5000")

    pdf.subheading("3. Frontend")
    pdf.code_block([
        "cd frontend",
        "npm install",
        "npm run dev",
    ])
    pdf.body("App: http://localhost:5173")

    pdf.section_title("Credentials Needed")
    pdf.subheading("Required (API will not start without these)")
    pdf.body("backend/.env")
    pdf.env_var("DATABASE_URL", "postgresql://user:pass@localhost:5432/gopostalsd_dev")
    pdf.env_var("SINALITE_CLIENT_ID", "Found at https://apifrontend_stage.sinaliteuppy.com/")
    pdf.env_var("SINALITE_CLIENT_SECRET", "Found at https://apifrontend_stage.sinaliteuppy.com/")
    pdf.env_var("FRONTEND_URL", "http://localhost:5173")
    pdf.ln(2)
    pdf.body(
        "SINALITE_BASE_URL_DEV and SINALITE_BASE_URL default to "
        "https://apiconnect.sinalite.com"
    )

    pdf.subheading("For full end-to-end flows (optional locally)")
    pdf.body("Email - pick one provider in backend/.env:")
    pdf.env_var("MAILERSEND_API_KEY", "OR")
    pdf.env_var("", "SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD")
    pdf.ln(2)

    pdf.body("Square checkout - backend/.env + frontend/.env:")
    pdf.env_var("SQUARE_ACCESS_TOKEN", "Found at https://developer.squareup.com/console/en/apps")
    pdf.env_var("SQUARE_APPLICATION_ID", "same value as VITE_SQUARE_APPLICATION_ID")
    pdf.env_var("SQUARE_LOCATION_ID", "same value as VITE_SQUARE_LOCATION_ID")
    pdf.env_var("SQUARE_ENVIRONMENT", "sandbox")
    pdf.ln(2)

    pdf.body("frontend/.env:")
    pdf.env_var("VITE_API_BASE_URL", "http://localhost:5000/api")
    pdf.env_var("VITE_SQUARE_APPLICATION_ID", " Found at https://developer.squareup.com/console/en/apps")
    pdf.env_var("VITE_SQUARE_LOCATION_ID", "Found at https://developer.squareup.com/console/en/apps")
    pdf.ln(2)

    pdf.subheading("Not needed for local dev")
    pdf.bullet("Supabase (uploads use backend/server/uploads/ locally)")

    pdf.output(str(OUTPUT))
    return OUTPUT


if __name__ == "__main__":
    path = build_pdf()
    print(f"Created {path}")
