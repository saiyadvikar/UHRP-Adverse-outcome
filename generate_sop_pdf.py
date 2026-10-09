import os
import sys
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

print("Building Complete SOP Document in PDF...")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            self.saveState()
            self.setStrokeColor(colors.HexColor("#1E1B4B"))
            self.setLineWidth(3)
            self.line(36, 805, 559, 805)
            self.restoreState()
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1E1B4B"))
        self.drawString(36, 808, "STANDARD OPERATING PROCEDURE (SOP)")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawRightString(559, 808, "Sankalp Clinical Audit & BMO Feedback Dashboard")
        
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 800, 559, 800)
        
        self.line(36, 45, 559, 45)
        self.setFont("Helvetica", 8)
        self.drawString(36, 32, "District Hospital Khargone (M.P.) | Department of Health & Family Welfare")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 32, page_str)
        self.restoreState()

pdf_path = "SOP_Adverse_Outcome_Feedback_Dashboard.pdf"
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=A4,
    leftMargin=36,
    rightMargin=36,
    topMargin=48,
    bottomMargin=52
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=colors.HexColor("#1E1B4B"),
    spaceAfter=5
)

subtitle_style = ParagraphStyle(
    "DocSubTitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10.5,
    leading=14,
    textColor=colors.HexColor("#4338CA"),
    spaceAfter=12
)

h1_style = ParagraphStyle(
    "SectionH1",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=colors.HexColor("#1E1B4B"),
    spaceBefore=12,
    spaceAfter=5,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    "SectionH2",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    textColor=colors.HexColor("#1E293B"),
    spaceBefore=9,
    spaceAfter=4,
    keepWithNext=True
)

body_style = ParagraphStyle(
    "BodyTextCustom",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11.5,
    textColor=colors.HexColor("#1E293B"),
    spaceAfter=5
)

bullet_style = ParagraphStyle(
    "BulletCustom",
    parent=body_style,
    leftIndent=12,
    firstLineIndent=-8,
    spaceAfter=3
)

callout_style = ParagraphStyle(
    "CalloutText",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11.5,
    textColor=colors.HexColor("#0F172A")
)

tbl_cell = ParagraphStyle(
    "TableCell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor("#1E293B")
)

tbl_cell_bold = ParagraphStyle(
    "TableCellBold",
    parent=tbl_cell,
    fontName="Helvetica-Bold"
)

tbl_hdr = ParagraphStyle(
    "TableHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=10.5,
    textColor=colors.white
)

code_style = ParagraphStyle(
    "CodeText",
    parent=styles["Normal"],
    fontName="Courier",
    fontSize=7.5,
    leading=9,
    textColor=colors.HexColor("#0F172A")
)

story = []

# COVER / HEADER
story.append(Spacer(1, 6))
story.append(Paragraph("STANDARD OPERATING PROCEDURE (SOP)", ParagraphStyle("SubHeaderMeta", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.HexColor("#4F46E5"), leading=11, spaceAfter=4)))
story.append(Paragraph("Adverse Pregnancy Outcome Clinical Audit & BMO Feedback Dashboard", title_style))
story.append(Paragraph("Operational Protocol for District Hospital Khargone & Peripheral Health Blocks (Madhya Pradesh)", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E1B4B"), spaceAfter=8))

meta_data = [
    [Paragraph("<b>Document Version:</b> 1.0 (Final)", tbl_cell), Paragraph("<b>Target District:</b> West Nimar (Khargone), M.P.", tbl_cell)],
    [Paragraph("<b>Author / Unit:</b> District QA & Sankalp Project Team", tbl_cell), Paragraph("<b>Nodal Facility:</b> District Hospital (DH) Khargone", tbl_cell)],
    [Paragraph("<b>Target Audience:</b> BMOs, MO I/Cs, CHOs, ANMs, BPMs, M&E", tbl_cell), Paragraph("<b>Effective Date:</b> September 2026 (Monthly Cycle)", tbl_cell)],
    [Paragraph("<b>Outputs:</b> Interactive HTML & 11-Tab Styled Excel Linelist", tbl_cell), Paragraph("<b>Mandate:</b> Zero Missed High-Risk ANC in Peripheral Care", tbl_cell)]
]
t_meta = Table(meta_data, colWidths=[260, 263])
t_meta.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("TOPPADDING", (0,0), (-1,-1), 3.5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
]))
story.append(t_meta)
story.append(Spacer(1, 10))

exec_summary_text = """<b>EXECUTIVE MANDATE &amp; OPERATIONAL CONTEXT:</b><br/>
Every month, pregnant women present to District Hospital Khargone with severe adverse pregnancy complications (Severe Preeclampsia, Eclampsia, Hb &lt; 7.0 g/dL, Sickle Cell Crisis, and Perinatal Death). An audit of clinical records reveals that over 70% of these adverse outcomes stem from missed screening, delayed risk identification, or absent pre-referral stabilization during peripheral Antenatal Care (ANC) at Sub-Health Centres (SHC), Health &amp; Wellness Centres (HWC), and Primary Health Centres (PHC).<br/><br/>
This SOP establishes the complete standard operating procedure for generating the <b>BMO Adverse Outcome Feedback Dashboard</b> and <b>11-Tab Styled Excel Linelist</b>. It enables the Chief Medical &amp; Health Officer (CMHO) and Block Medical Officers (BMOs) to trace each tertiary complication back to its assigned Subcentre and frontline workers (ANM, CHO, ASHA) and enforce corrective actions."""

t_exec = Table([[Paragraph(exec_summary_text, callout_style)]], colWidths=[523])
t_exec.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#EEF2FF")),
    ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#6366F1")),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
story.append(t_exec)
story.append(Spacer(1, 12))
# SECTION 1: CLINICAL DEFINITIONS
story.append(Paragraph("1. Clinical Definitions & Analytical Framework", h1_style))
story.append(Paragraph("This SOP establishes precise clinical definitions, diagnostic thresholds, algorithmic detection rules, and peripheral care preventative imperatives used in the audit system:", body_style))

clinical_defs = [
    [
        Paragraph("Clinical Condition & Threshold", tbl_hdr),
        Paragraph("Detection Rule (Regex)", tbl_hdr),
        Paragraph("Diagnostic Criteria & ANC Quality Gap Rationale", tbl_hdr)
    ],
    [
        Paragraph("<b>Severe Preeclampsia / PIH</b><br/>BP &ge; 160/110 mmHg on 2 occasions with proteinuria (&ge; 2+) after 20 weeks, or gestational hypertension with end-organ dysfunction (headache, vision blur, epigastric pain).", tbl_cell),
        Paragraph("<code>preeclampsia|<br/>pre eclampsia|<br/>pih</code>", code_style),
        Paragraph("Reflects missed weekly BP screening at HWC/PHC and absence of oral anti-hypertensives (Labetalol / Methyldopa) in peripheral care.", tbl_cell)
    ],
    [
        Paragraph("<b>Hypertensive Disorders (Eclampsia)</b><br/>Generalized tonic-clonic convulsions or coma in a preeclamptic woman without other neurological causes.", tbl_cell),
        Paragraph("<code>convulsion|<br/>(?&lt;!pre\\s)<br/>(?&lt;!pre)eclampsia</code>", code_style),
        Paragraph("Demonstrates absence of pre-referral stabilization: <b>failure to administer loading dose of Magnesium Sulfate (Inj. MgSO4 4g IV + 10g IM)</b> before ambulance transfer.", tbl_cell)
    ],
    [
        Paragraph("<b>Severe Anemia</b><br/>Hemoglobin level &lt; 7.0 g/dL during pregnancy (critical values &lt; 4.0 g/dL).", tbl_cell),
        Paragraph("<code>anemia|<br/>anaemia</code>", code_style),
        Paragraph("Reflects missed early registration, unverified IFA consumption, or failure to administer <b>IV Iron Sucrose or Inj. FCM</b> in 2nd/3rd trimester at CHC/PHC.", tbl_cell)
    ],
    [
        Paragraph("<b>Sickle Cell Disease Crisis</b><br/>Vaso-occlusive pain crisis, acute chest syndrome, or severe hemolytic crisis in HbSS or HbS-&beta; thalassemia patients.", tbl_cell),
        Paragraph("<code>scd|<br/>sickle</code>", code_style),
        Paragraph("Prevalent tribal complication. Indicates missed universal screening under MP Sickle Cell Mission, lack of 5mg daily Folic Acid, and unmonitored dehydration.", tbl_cell)
    ],
    [
        Paragraph("<b>Perinatal Loss (Stillbirth / IUFD)</b><br/>Fetal demise at &ge; 28 weeks of gestation (or birth weight &ge; 1000g).", tbl_cell),
        Paragraph("<code>iud|iufd|<br/>stillbirth|msb</code>", code_style),
        Paragraph("Direct indicator of missed fetal heart sound monitoring, unaddressed IUGR, severe oligohydramnios, or undetected fetal distress.", tbl_cell)
    ],
    [
        Paragraph("<b>Early Neonatal Death</b><br/>Death of a live-born infant within 7 completed days of life (0–168 hours).", tbl_cell),
        Paragraph("<code>died|death</code><br/>in baby status", code_style),
        Paragraph("Attributable to severe intrapartum birth asphyxia, meconium aspiration, hypothermia during transport, or extreme prematurity.", tbl_cell)
    ],
    [
        Paragraph("<b>SNCU Transfer / Admission</b><br/>Transfer of neonate to Special Newborn Care Unit within hours of delivery.", tbl_cell),
        Paragraph("<code>yes|shift|lbw|<br/>gasping|msl</code>", code_style),
        Paragraph("Primary reasons: Meconium Stained Liquor (MSL), birth weight &lt; 1800g, respiratory distress, prematurity, or sepsis.", tbl_cell)
    ],
    [
        Paragraph("<b>Maternal Death &amp; Near-Miss</b><br/>Maternal death during pregnancy/puerperium; or near-fatal collapse requiring tertiary transfer (MY Hospital Indore).", tbl_cell),
        Paragraph("<code>died|death|<br/>refer|indore</code>", code_style),
        Paragraph("Terminal indicators of delayed danger sign recognition (Delay 1), transport delay (Delay 2), or delayed resuscitation (Delay 3).", tbl_cell)
    ],
    [
        Paragraph("<b>HRP Flagged in ANMOL</b><br/>Whether patient was formally registered and flagged as High Risk on portal.", tbl_cell),
        Paragraph("Cross-match with HRP report", code_style),
        Paragraph("Audits frontline tracking compliance. If a mother with severe complications was unflagged, it represents an administrative tracking failure.", tbl_cell)
    ]
]

t_clin = Table(clinical_defs, colWidths=[165, 95, 263])
t_clin.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E1B4B")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("TOPPADDING", (0,0), (-1,-1), 3),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
]))
story.append(t_clin)
story.append(Spacer(1, 8))

delays_text = """<b>THE THREE DELAYS AUDIT FRAMEWORK:</b><br/>
All adverse cases must be audited through the Three Delays model during monthly BMO reviews:
&bull; <b>Delay 1 (Care Seeking):</b> Family/mother delayed in recognizing danger signs (e.g. severe headache, blurred vision, absent fetal movement).<br/>
&bull; <b>Delay 2 (Transport / Referral):</b> Delay in reaching the referral hospital due to ambulance availability, bad terrain, or multiple intermediate stops.<br/>
&bull; <b>Delay 3 (Facility Protocol):</b> Delay in receiving timely, standardized clinical care at the facility (lack of MgSO4, IV iron, or blood products).<br/>"""
t_del = Table([[Paragraph(delays_text, callout_style)]], colWidths=[523])
t_del.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
    ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#F59E0B")),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
story.append(t_del)
story.append(PageBreak())
# SECTION 2: DATA SOURCES & VARIABLE MAPPING
story.append(Paragraph("2. Data Sources & Complete Variable Dictionary", h1_style))
story.append(Paragraph("The audit pipeline ingests four foundational datasets. Below is the complete variable dictionary detailing every file, sheet name, column letter, column index, header name, data type, and its operational role:", body_style))

story.append(Paragraph("2.1 Primary Adverse Outcome Register (DH Delivery Register)", h2_style))
story.append(Paragraph("<b>Source File:</b> <code>Data/Adverse outcome linelist.xlsx</code> | <b>Sheet:</b> <code>Sheet1</code> | <b>Header Row:</b> 1 (Index 0)", body_style))

dh_dict = [
    [Paragraph("Col", tbl_hdr), Paragraph("Index", tbl_hdr), Paragraph("Source Header Name", tbl_hdr), Paragraph("Data Type", tbl_hdr), Paragraph("Operational Role & Standardization Rule", tbl_hdr)],
    [Paragraph("A", tbl_cell_bold), Paragraph("0", tbl_cell), Paragraph("Sr No", tbl_cell_bold), Paragraph("Integer", tbl_cell), Paragraph("Case sequential identifier (1 to N). Primary audit tracking ID.", tbl_cell)],
    [Paragraph("B", tbl_cell_bold), Paragraph("1", tbl_cell), Paragraph("MPID", tbl_cell_bold), Paragraph("String/Float", tbl_cell), Paragraph("RCH portal Maternal ID. Cleaned by stripping '.0', 'nan', 'direct entry'. Used as primary key for registry cross-matching.", tbl_cell)],
    [Paragraph("C", tbl_cell_bold), Paragraph("2", tbl_cell), Paragraph("Admission date", tbl_cell_bold), Paragraph("Datetime", tbl_cell), Paragraph("Date of DH admission. Parsed into 'YYYY-MM-DD' and 'Month YYYY' for dynamic filtering.", tbl_cell)],
    [Paragraph("D", tbl_cell_bold), Paragraph("3", tbl_cell), Paragraph("Patient Name ", tbl_cell_bold), Paragraph("String", tbl_cell), Paragraph("Name of pregnant woman and husband (e.g. 'Chena bai/Indarsingh'). Trailing spaces trimmed.", tbl_cell)],
    [Paragraph("E", tbl_cell_bold), Paragraph("4", tbl_cell), Paragraph("Address ", tbl_cell_bold), Paragraph("String", tbl_cell), Paragraph("Stated village / locality address. Used in secondary fuzzy location triangulation.", tbl_cell)],
    [Paragraph("F", tbl_cell_bold), Paragraph("5", tbl_cell), Paragraph("village ", tbl_cell_bold), Paragraph("String", tbl_cell), Paragraph("Stated revenue village name.", tbl_cell)],
    [Paragraph("G", tbl_cell_bold), Paragraph("6", tbl_cell), Paragraph("Sub centre ", tbl_cell_bold), Paragraph("String", tbl_cell), Paragraph("Stated Subcentre / referring peripheral facility (e.g. 'phc oon', 'chc Bhagwanpura').", tbl_cell)],
    [Paragraph("H", tbl_cell_bold), Paragraph("7", tbl_cell), Paragraph("Block", tbl_cell_bold), Paragraph("String", tbl_cell), Paragraph("Stated health block name. Used for initial block classification before hierarchy validation.", tbl_cell)],
    [Paragraph("I", tbl_cell_bold), Paragraph("8", tbl_cell), Paragraph("Diagnosis ", tbl_cell_bold), Paragraph("String", tbl_cell), Paragraph("Clinical diagnosis text recorded by DH obstetric team. Parsed via regex into 4 core categories.", tbl_cell)],
    [Paragraph("J", tbl_cell_bold), Paragraph("9", tbl_cell), Paragraph("Mother status", tbl_cell_bold), Paragraph("String", tbl_cell), Paragraph("Maternal status at discharge ('live', 'died', 'refer indore'). Classified into Live / Maternal Death / Referral.", tbl_cell)],
    [Paragraph("K", tbl_cell_bold), Paragraph("10", tbl_cell), Paragraph("Baby status ", tbl_cell_bold), Paragraph("String", tbl_cell), Paragraph("Perinatal delivery outcome ('live', 'iud', 'died'). Classified into Live Birth / Stillbirth (IUFD) / Neonatal Death.", tbl_cell)],
    [Paragraph("L", tbl_cell_bold), Paragraph("11", tbl_cell), Paragraph("Transfer of baby to sncu reason ", tbl_cell_bold), Paragraph("String", tbl_cell), Paragraph("Indicates whether baby was transferred to SNCU and clinical justification (MSL, gasping, LBW, prematurity).", tbl_cell)],
    [Paragraph("M", tbl_cell_bold), Paragraph("12", tbl_cell), Paragraph("mob num", tbl_cell_bold), Paragraph("String/Float", tbl_cell), Paragraph("Patient/family mobile number. Cleaned to 10 digits. Used as secondary cross-match key when MPID is missing.", tbl_cell)]
]
t_dh = Table(dh_dict, colWidths=[24, 28, 125, 66, 280])
t_dh.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E1B4B")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("TOPPADDING", (0,0), (-1,-1), 2.5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 2.5),
]))
story.append(t_dh)
story.append(Spacer(1, 8))

story.append(Paragraph("2.2 ANC Line List Registry Report", h2_style))
story.append(Paragraph("<b>Source File:</b> <code>Data/ANC_Line_list_Report_2026-09-17_09_45_52.xlsx</code> | <b>Header Row:</b> 9 (<code>skiprows=8</code>) | <b>Total Columns:</b> 180", body_style))

anc_dict = [
    [Paragraph("Col Header Name", tbl_hdr), Paragraph("Col Index", tbl_hdr), Paragraph("Data Type", tbl_hdr), Paragraph("Analytical Purpose & Matching Role in Dashboard", tbl_hdr)],
    [Paragraph("Health Block Name", tbl_cell_bold), Paragraph("3", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Authoritative health block where patient is enrolled. Overrides inaccurate stated block.", tbl_cell)],
    [Paragraph("Health Sub Centre Name", tbl_cell_bold), Paragraph("5", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Authoritative Sub-Health Centre (SHC). Used to join with staff contact numbers.", tbl_cell)],
    [Paragraph("Village Name", tbl_cell_bold), Paragraph("6", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Enrolled revenue village name. Used for community audit tracing.", tbl_cell)],
    [Paragraph("Name of ANM", tbl_cell_bold), Paragraph("7", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Assigned Auxiliary Nurse Midwife responsible for antenatal tracking.", tbl_cell)],
    [Paragraph("Name of ASHA", tbl_cell_bold), Paragraph("8", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Assigned Accredited Social Health Activist for village home visits.", tbl_cell)],
    [Paragraph("CHO Name", tbl_cell_bold), Paragraph("9", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Assigned Community Health Officer at Health & Wellness Centre.", tbl_cell)],
    [Paragraph("Name of Pregnant Woman", tbl_cell_bold), Paragraph("10", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Enrolled pregnant woman name. Cross-verified with DH admission name.", tbl_cell)],
    [Paragraph("MP ID", tbl_cell_bold), Paragraph("11", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Primary matching key. Exact 11-digit maternal registration ID.", tbl_cell)],
    [Paragraph("Mobile Number", tbl_cell_bold), Paragraph("17", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Cleaned 10-digit mobile number. Secondary fallback matching key.", tbl_cell)],
    [Paragraph("HRP Identified(Yes/No)", tbl_cell_bold), Paragraph("22", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Whether patient was identified as High Risk Pregnancy during routine ANC.", tbl_cell)],
    [Paragraph("Hb.1 - Hb.11 / BP.1 - .11", tbl_cell_bold), Paragraph("Various", tbl_cell), Paragraph("Floats/Strings", tbl_cell), Paragraph("Serial hemoglobin measurements and blood pressure checks to track clinical trajectory.", tbl_cell)]
]
t_anc = Table(anc_dict, colWidths=[150, 48, 65, 260])
t_anc.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E1B4B")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("TOPPADDING", (0,0), (-1,-1), 2.5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 2.5),
]))
story.append(t_anc)
story.append(PageBreak())
story.append(Paragraph("2.3 High Risk Pregnancy (HRP/UHRP) Line List Report", h2_style))
story.append(Paragraph("<b>Source File:</b> <code>Data/HRP_Line_List_Report_2026-09-17_10_22_24.xlsx</code> | <b>Header Row:</b> 8 (<code>skiprows=7</code>) | <b>Total Columns:</b> 76", body_style))

hrp_dict = [
    [Paragraph("Col Header Name", tbl_hdr), Paragraph("Col Index", tbl_hdr), Paragraph("Data Type", tbl_hdr), Paragraph("Analytical Role & Clinical Extraction Rule", tbl_hdr)],
    [Paragraph("Health Block Name", tbl_cell_bold), Paragraph("3", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Authoritative health block name for confirmed high-risk cases.", tbl_cell)],
    [Paragraph("Health Sub Centre Name", tbl_cell_bold), Paragraph("5", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Authoritative subcentre for frontline staff linkage.", tbl_cell)],
    [Paragraph("MP ID", tbl_cell_bold), Paragraph("11", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Primary matching key to link adverse outcomes with confirmed high-risk registry.", tbl_cell)],
    [Paragraph("Mobile Number", tbl_cell_bold), Paragraph("17", tbl_cell), Paragraph("String", tbl_cell), Paragraph("10-digit mobile fallback key for patient reconciliation.", tbl_cell)],
    [Paragraph("Identified with PIH (Yes/No)", tbl_cell_bold), Paragraph("42", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Identifies whether pregnancy-induced hypertension was flagged on the portal.", tbl_cell)],
    [Paragraph("PIH Management Done", tbl_cell_bold), Paragraph("43", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Records anti-hypertensive regimen administered (Methyldopa, Labetalol, Inj. MgSO4).", tbl_cell)],
    [Paragraph("If severe anemia (Yes/No)", tbl_cell_bold), Paragraph("33", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Flags clinical severe anemia enrollment on portal.", tbl_cell)],
    [Paragraph("Inj FCM given (Yes/No)", tbl_cell_bold), Paragraph("40", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Verifies whether IV Ferric Carboxymaltose was administered at facility.", tbl_cell)],
    [Paragraph("Number of Blood transfusion units", tbl_cell_bold), Paragraph("39", tbl_cell), Paragraph("String/Float", tbl_cell), Paragraph("Quantity of packed red cells/whole blood transfused before delivery.", tbl_cell)],
    [Paragraph("Result of sickle cell test", tbl_cell_bold), Paragraph("22", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Result of solubility/electrophoresis test (Trait, Disease, Thalassemia, Negative).", tbl_cell)],
    [Paragraph("GDM Positive / Management", tbl_cell_bold), Paragraph("44, 45", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Gestational diabetes screening status and medical nutrition/insulin therapy.", tbl_cell)],
    [Paragraph("Previous LSCS", tbl_cell_bold), Paragraph("29", tbl_cell), Paragraph("String", tbl_cell), Paragraph("Prior lower segment cesarean delivery. High risk indicator.", tbl_cell)]
]
t_hrp = Table(hrp_dict, colWidths=[150, 48, 65, 260])
t_hrp.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E1B4B")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("TOPPADDING", (0,0), (-1,-1), 2.5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 2.5),
]))
story.append(t_hrp)
story.append(Spacer(1, 8))

story.append(Paragraph("2.4 Master Location & Human Resources Hierarchy", h2_style))
story.append(Paragraph("<b>Source File:</b> <code>Resources/Location Hirarchy.xlsx</code> | Contains 4 official directories used for facility and personnel linkage:", body_style))

loc_dict = [
    [Paragraph("Sheet Name", tbl_hdr), Paragraph("Header Row", tbl_hdr), Paragraph("Key Columns Used", tbl_hdr), Paragraph("Functional Integration in Pipeline", tbl_hdr)],
    [
        Paragraph("<b>Village list</b>", tbl_cell_bold),
        Paragraph("Row 2 (skip=1)", tbl_cell),
        Paragraph("Col B: District Name<br/>Col D: Block Name<br/>Col G: Facility Name<br/>Col K: Subcentre Name<br/>Col O: Village Name", tbl_cell),
        Paragraph("Authoritative location tree across all 9 blocks of Khargone. Used to resolve unbooked/unregistered cases by matching stated village names to official Subcentres and Blocks.", tbl_cell)
    ],
    [
        Paragraph("<b>ANM</b>", tbl_cell_bold),
        Paragraph("Row 3 (skip=2)", tbl_cell),
        Paragraph("Col C: Block Name<br/>Col E: Sub-Health Facility<br/>Col F: ANM Name<br/>Col H: Contact No", tbl_cell),
        Paragraph("Master roster of 339 Auxiliary Nurse Midwives. Joined on normalized Subcentre name (or ANM Name) to retrieve verified 10-digit mobile contact numbers.", tbl_cell)
    ],
    [
        Paragraph("<b>CHO</b>", tbl_cell_bold),
        Paragraph("Row 3 (skip=2)", tbl_cell),
        Paragraph("Col C: Block Name<br/>Col E: Sub Health Facility<br/>Col F: Name of CHO<br/>Col H: Contact No", tbl_cell),
        Paragraph("Master roster of 284 Community Health Officers at HWCs. Joined on normalized Subcentre name (or CHO Name) to retrieve verified mobile contact numbers.", tbl_cell)
    ],
    [
        Paragraph("<b>HR Directory</b>", tbl_cell_bold),
        Paragraph("Row 1 (skip=0)", tbl_cell),
        Paragraph("Col B: Facility Name<br/>Col E: HR Name<br/>Col F: Designation<br/>Col I: Mobile Number", tbl_cell),
        Paragraph("Secondary human resources verification file used when ANM or CHO contact numbers are missing or updated in field postings.", tbl_cell)
    ]
]
t_loc = Table(loc_dict, colWidths=[90, 75, 138, 220])
t_loc.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E1B4B")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("TOPPADDING", (0,0), (-1,-1), 3),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
]))
story.append(t_loc)
story.append(PageBreak())
# SECTION 3: MULTI-TIERED MATCHING ENGINE
story.append(Paragraph("3. Multi-Tiered Data Triangulation & Matching Engine", h1_style))
story.append(Paragraph("To ensure zero patient leakage and complete spatial reconciliation, <code>process_data.py</code> implements a robust 6-tier hierarchical matching algorithm:", body_style))

tier_data = [
    [Paragraph("Matching Tier", tbl_hdr), Paragraph("Match Logic & Input Fields", tbl_hdr), Paragraph("Reconciliation Output & Impact", tbl_hdr)],
    [
        Paragraph("<b>Tier 1: Universal MP ID Matching</b>", tbl_cell_bold),
        Paragraph("Exact join on cleaned 11-digit <code>MPID</code> against ANC &amp; HRP registries.", tbl_cell),
        Paragraph("Highest confidence match. Instantly retrieves verified Health Block, Subcentre, Village, registered ANM/CHO/ASHA, and portal clinical tracking history.", tbl_cell)
    ],
    [
        Paragraph("<b>Tier 2: Clean Mobile Phone Fallback</b>", tbl_cell_bold),
        Paragraph("Join on stripped 10-digit <code>mob num</code> against ANC &amp; HRP registries when MPID is missing or recorded as 'direct entry'.", tbl_cell),
        Paragraph("Resolves direct hospital walk-ins who possessed portal registrations under their husband or family contact number.", tbl_cell)
    ],
    [
        Paragraph("<b>Tier 3: Location Hierarchy Subcentre Join</b>", tbl_cell_bold),
        Paragraph("Normalize verified Subcentre string (stripping 'SHC', 'PHC', 'New', punctuation, and spaces) and join against <code>ANM</code> &amp; <code>CHO</code> sheets.", tbl_cell),
        Paragraph("Pulls official ANM Name, ANM Contact Number, CHO Name, and CHO Contact Number directly into the patient linelist.", tbl_cell)
    ],
    [
        Paragraph("<b>Tier 4: Personnel Name Fallback</b>", tbl_cell_bold),
        Paragraph("Normalize ANM Name / CHO Name from registry and search <code>anm_by_name</code> / <code>cho_by_name</code> hash maps.", tbl_cell),
        Paragraph("Retrieves active phone numbers even if subcentre naming conventions differ between portal dumps and HR directories.", tbl_cell)
    ],
    [
        Paragraph("<b>Tier 5: Village Text Extraction (Unbooked Cases)</b>", tbl_cell_bold),
        Paragraph("For unbooked walk-ins, extract geographic words from <code>Address</code> and <code>village</code>, join against <code>Village list</code> master.", tbl_cell),
        Paragraph("Locates the exact administrative Subcentre and Block for mothers who bypassed peripheral care (e.g. Tharadpura &rarr; SHC Ambakheda in Bhagwanpura).", tbl_cell)
    ],
    [
        Paragraph("<b>Tier 6: Out-of-District Classification</b>", tbl_cell_bold),
        Paragraph("Identify geographic tokens outside Khargone: Sendhwa, Thikri, Rajpur, Nepanagar, Dahinala, Dharampuri, Punasa, Jalgaon.", tbl_cell),
        Paragraph("Segregates external inflow cases into 'Out of District' block tagged by origin (Barwani, Burhanpur, Dhar, Khandwa, Maharashtra) to preserve Khargone block KPI integrity.", tbl_cell)
    ]
]
t_tier = Table(tier_data, colWidths=[120, 163, 240])
t_tier.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E1B4B")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("TOPPADDING", (0,0), (-1,-1), 3.5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
]))
story.append(t_tier)
story.append(Spacer(1, 10))

# SECTION 4: DELIVERABLE SPECIFICATIONS
story.append(Paragraph("4. Technical Specifications of Deliverables", h1_style))

story.append(Paragraph("4.1 Interactive Web Dashboard (<code>BMO_Adverse_Outcome_Dashboard.html</code>)", h2_style))
story.append(Paragraph("&bull; <b>Single Action Header:</b> Contains print trigger and strictly <b>1 global download button</b> (<code>Download Excel Report</code>) linking directly to the styled multi-tab workbook.<br/>", bullet_style))
story.append(Paragraph("&bull; <b>Prominent Filter Strip:</b> Instant client-side filtering by Block (All, Khargone Only, 9 individual blocks, Out of District), Admission Month, Clinical Complication, and Multi-field search.<br/>", bullet_style))
story.append(Paragraph("&bull; <b>Dynamic 6 KPI Cards:</b> Auto-recalculating metrics (Total Cases, Khargone Cases, Out of District, HDP/Eclampsia, Severe Anemia, Perinatal Loss). HRP enrolled card omitted as directed.<br/>", bullet_style))
story.append(Paragraph("&bull; <b>Exact Tab Order:</b> 1. Block Scorecard &amp; Hierarchy &rarr; 2. Patient Linelist &rarr; 3. Out of District Inflow &rarr; 4. Overview &amp; Gaps (Three Delays chart omitted) &rarr; 5. BMO Action Guidelines.<br/>", bullet_style))
story.append(Paragraph("&bull; <b>Linelist Table Formatting:</b> Columns arranged as: <i>Assigned Block &amp; Subcentre &rarr; Patient &amp; ID &rarr; Date of Admission &rarr; DH Diagnosis &rarr; HRP flagged in ANMOL &rarr; Perinatal/Maternal Outcome &rarr; Frontline Workers (with click-to-call phone badges) &rarr; Action Review</i>. Click-to-sort enabled across all columns.<br/>", bullet_style))
story.append(Paragraph("&bull; <b>Case Modal Dossier:</b> Detailed patient clinical profile, high-risk flags, 3-column staff card with direct <code>tel:</code> dial links, and the 3 concise BMO Action Directives.<br/>", bullet_style))

story.append(Spacer(1, 6))
story.append(Paragraph("4.2 Formatted Excel Linelist (<code>Adverse_Outcome_Patient_Linelist_Styled.xlsx</code>)", h2_style))
story.append(Paragraph("Generated via <code>openpyxl</code> with strict layout and color styling identical to the web dashboard:", body_style))

excel_specs = [
    [Paragraph("Component / Tab", tbl_hdr), Paragraph("Exact Tab Order & Column Structure", tbl_hdr), Paragraph("Color Profile & Hex Styling", tbl_hdr)],
    [
        Paragraph("<b>Tab 1: Block Scorecard</b><br/>(1st Place)", tbl_cell_bold),
        Paragraph("Scorecard of all 9 Khargone blocks with columns: Block Name, Total Adverse, Severe Preeclamp, Eclampsia, Severe Anemia, Sickle cell crisis, Stillbirths, SNCU transfer, Neo Deaths, plus Total Khargone District row.", tbl_cell),
        Paragraph("Header fill: Deep Indigo <code>#1E1B4B</code>, White bold text.<br/>Total row fill: Slate <code>#E2E8F0</code>, text <code>#0F172A</code>.", tbl_cell)
    ],
    [
        Paragraph("<b>Tabs 2 to 10: Block Linelists</b><br/>(Separate Tab per Block)", tbl_cell_bold),
        Paragraph("Separate dedicated tab for each Khargone block: <b>Barwaha</b> (8), <b>Bhagwanpura</b> (10), <b>Bhikangaon</b> (4), <b>Gogaon</b> (4), <b>Jhiranya</b> (7), <b>Kasrawad</b> (1), <b>Khargone</b> (5), <b>Maheshwar</b> (2), <b>Segaon</b> (5).<br/><b>Strictly 16 Columns (Col A to P):</b><br/>Sr No, Assigned Block, Assigned Subcentre, Village/Area, Patient Name, Mobile Number, MP ID, Date of Admission, Admission Month, DH Diagnosis, Clinical Category, HRP flagged in ANMOL, HRP High Risk Category, Perinatal Outcome, Mother Status, SNCU Transfer.<br/><b>All columns after SNCU Transfer (Q to W) removed.</b>", tbl_cell),
        Paragraph("<b>Clinical Diagnosis Fills:</b><br/>&bull; Severe Preeclampsia: <code>#FEF3C7</code> (Text <code>#92400E</code>)<br/>&bull; Eclampsia: <code>#FEE2E2</code> (Text <code>#991B1B</code>)<br/>&bull; Severe Anemia: <code>#EDE9FE</code> (Text <code>#5B21B6</code>)<br/>&bull; Sickle Cell Crisis: <code>#FFEDD5</code> (Text <code>#9A3412</code>)<br/><br/><b>Outcomes &amp; HRP Fills:</b><br/>&bull; Live Birth: <code>#DCFCE7</code> (Text <code>#166534</code>)<br/>&bull; Stillbirth: <code>#F1F5F9</code> (Text <code>#475569</code>)<br/>&bull; Neonatal Death: <code>#FEE2E2</code> (Text <code>#991B1B</code>)<br/>&bull; Maternal Death: <code>#991B1B</code> (Text <code>#FFFFFF</code>)<br/>&bull; HRP Flagged: <code>#ECFDF5</code> (Text <code>#047857</code>)<br/>&bull; Not in HRP: <code>#FFF1F2</code> (Text <code>#BE123C</code>)<br/>&bull; SNCU Yes: <code>#E0E7FF</code> (Text <code>#3730A3</code>)", tbl_cell)
    ],
    [
        Paragraph("<b>Tab 11: Out of District Inflow</b><br/>(Last Tab)", tbl_cell_bold),
        Paragraph("External referral admissions from Barwani, Dhar, Burhanpur, Khandwa, and Maharashtra (10 cases). Same standardized 16 columns (Col A to P).", tbl_cell),
        Paragraph("Assigned block cell styled with Light Amber fill <code>#FFFBEB</code> and text <code>#B45309</code>.", tbl_cell)
    ]
]
t_xls = Table(excel_specs, colWidths=[110, 233, 180])
t_xls.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E1B4B")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("TOPPADDING", (0,0), (-1,-1), 3),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
]))
story.append(t_xls)
story.append(PageBreak())
# SECTION 5: STEP-BY-STEP OPERATIONAL SOP WORKFLOW
story.append(Paragraph("5. Step-by-Step Monthly Operational SOP Workflow", h1_style))
story.append(Paragraph("District Health Teams, Hospital Data Officers, and BMOs must execute the following protocol between the 1st and 15th of every month:", body_style))

sop_steps = [
    [Paragraph("Timeline & Phase", tbl_hdr), Paragraph("Responsible Officer", tbl_hdr), Paragraph("Standard Operating Procedure Instructions", tbl_hdr)],
    [
        Paragraph("<b>Phase 1:<br/>1st–3rd of Month</b><br/>Data Ingestion", tbl_cell_bold),
        Paragraph("DH Delivery Room In-charge &amp; SNCU Data Entry Operator", tbl_cell),
        Paragraph("1. Export monthly delivery and maternal admission registers from District Hospital Khargone.<br/>2. Populate <code>Data/Adverse outcome linelist.xlsx</code> with mandatory fields: Sr No, MPID, Admission date, Patient Name, Address, village, Sub centre, Block, Diagnosis, Mother status, Baby status, Transfer of baby to sncu reason, and mob num.<br/>3. Ensure clean 10-digit mobile numbers are recorded for direct walk-ins lacking MPID.", tbl_cell)
    ],
    [
        Paragraph("<b>Phase 2:<br/>4th–5th of Month</b><br/>Portal Dump Extraction", tbl_cell_bold),
        Paragraph("District Data Officer / NHM M&amp;E Consultant", tbl_cell),
        Paragraph("1. Log into ANMOL/RCH portal and download cumulative ANC Line list Report for the previous month (&rarr; <code>Data/ANC_Line_list_Report_YYYY-MM-DD.xlsx</code>).<br/>2. Download the High Risk Pregnancy Line list Report (&rarr; <code>Data/HRP_Line_List_Report_YYYY-MM-DD.xlsx</code>).<br/>3. Verify that <code>Resources/Location Hirarchy.xlsx</code> reflects the latest staff postings.", tbl_cell)
    ],
    [
        Paragraph("<b>Phase 3:<br/>6th of Month</b><br/>Automated Processing", tbl_cell_bold),
        Paragraph("District MIS Unit / Systems Analyst", tbl_cell),
        Paragraph("Execute terminal processing commands in the project directory:<br/><code>python process_data.py</code> &rarr; Reconciles MPIDs, cross-matches registries, matches Location Hierarchy staff, outputs <code>bmo_dashboard_data.json</code>.<br/><code>python generate_styled_excel.py</code> &rarr; Produces 11-tab styled Excel workbook <code>Adverse_Outcome_Patient_Linelist_Styled.xlsx</code>.<br/><code>python scratch/update_html.py</code> &rarr; Updates web dashboard HTML payload.", tbl_cell)
    ],
    [
        Paragraph("<b>Phase 4:<br/>7th–8th of Month</b><br/>Data Verification &amp; QC", tbl_cell_bold),
        Paragraph("Civil Surgeon &amp; District Quality Assurance Officer", tbl_cell),
        Paragraph("1. Open <code>BMO_Adverse_Outcome_Dashboard.html</code> in any modern browser.<br/>2. Validate that total admissions equal DH registry count (56 cases).<br/>3. Check block distributions in Scorecard tab.<br/>4. Click <code>[Download Excel Report]</code> to ensure workbook contains 11 tabs, Block Scorecard is in 1st place, and all columns after SNCU transfer (Q to W) are absent.", tbl_cell)
    ],
    [
        Paragraph("<b>Phase 5:<br/>9th–10th of Month</b><br/>BMO Packet Dispatch", tbl_cell_bold),
        Paragraph("Chief Medical &amp; Health Officer (CMHO)", tbl_cell),
        Paragraph("1. Email the interactive HTML dashboard to all 9 Block Medical Officers.<br/>2. Attach the respective block's styled Excel sheet to each BMO.<br/>3. Issue formal audit meeting notice for the mid-month sector review.", tbl_cell)
    ],
    [
        Paragraph("<b>Phase 6:<br/>15th of Month</b><br/>Monthly Block Audit Meeting", tbl_cell_bold),
        Paragraph("BMO, Sector Medical Officers &amp; CHOs", tbl_cell),
        Paragraph("Enforce the <b>3 Mandatory BMO Action Directives:</b><br/><b>1. Do community audit why condition was not resolved?</b> Conduct field visits with ASHA/ANM to identify care-seeking delays (Delay 1).<br/><b>2. Ask in review meeting to MO and CHO why women presented with adverse outcome?</b> Table specific patient names from linelist. Query CHO/ANM on missed BP/Hb monitoring and lack of pre-referral stabilization (Delay 3).<br/><b>3. If found any system gaps try to resolve.</b> Restock IV Iron Sucrose/FCM, MgSO4, functional BP instruments, and enforce universal Sickle Cell screening.", tbl_cell)
    ]
]
t_sop = Table(sop_steps, colWidths=[100, 110, 313])
t_sop.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E1B4B")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("TOPPADDING", (0,0), (-1,-1), 3.5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
]))
story.append(t_sop)
story.append(Spacer(1, 10))

# SECTION 6: APPROVAL & SIGN-OFF
story.append(Paragraph("6. Document Approval & Governance Sign-off", h1_style))
signoff_data = [
    [Paragraph("Role / Governance Designation", tbl_hdr), Paragraph("Office / Institution", tbl_hdr), Paragraph("Signature &amp; Official Seal", tbl_hdr)],
    [Paragraph("Civil Surgeon / Hospital Superintendent", tbl_cell_bold), Paragraph("District Hospital Khargone (M.P.)", tbl_cell), Paragraph("________________________", tbl_cell)],
    [Paragraph("Chief Medical &amp; Health Officer (CMHO)", tbl_cell_bold), Paragraph("Department of Health &amp; Family Welfare, Khargone", tbl_cell), Paragraph("________________________", tbl_cell)],
    [Paragraph("District Nodal Officer (Maternal Health / NHM)", tbl_cell_bold), Paragraph("National Health Mission, Khargone", tbl_cell), Paragraph("________________________", tbl_cell)]
]
t_sign = Table(signoff_data, colWidths=[170, 180, 173])
t_sign.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E1B4B")),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(t_sign)

# Build PDF using NumberedCanvas
doc.build(story, canvasmaker=NumberedCanvas)
print(f"SUCCESS: Generated SOP PDF at: {pdf_path}")

# Copy to Resources/
res_pdf_path = os.path.join("Resources", pdf_path)
shutil.copyfile(pdf_path, res_pdf_path)
print(f"SUCCESS: Copied SOP PDF to: {res_pdf_path}")
