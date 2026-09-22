#!/usr/bin/env python3
"""Generate Beacon CMMC / NIST SP 800-171 readiness checklist PDF."""
from pathlib import Path
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parents[1] / 'downloads' / 'beacon-cmmc-readiness-checklist.pdf'
NAVY = HexColor('#1B2A4A')
SAGE = HexColor('#7A9E7E')
CREAM = HexColor('#F5F0E6')
SLATE = HexColor('#3D4A5C')
LIGHT = HexColor('#E8EEF2')

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._states = []
    def showPage(self):
        self._states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        n = len(self._states)
        for st in self._states:
            self.__dict__.update(st)
            self.setFillColor(NAVY)
            self.rect(0, letter[1] - 28, letter[0], 28, fill=1, stroke=0)
            self.setFillColor(white)
            self.setFont('Helvetica-Bold', 9)
            self.drawString(0.75*inch, letter[1] - 18, 'BEACON  ·  Canopy Harbor LLC')
            self.setFont('Helvetica', 8)
            self.drawRightString(letter[0] - 0.75*inch, letter[1] - 18, 'NIST SP 800-171 / CMMC Readiness Checklist')
            self.setFillColor(SAGE)
            self.rect(0, 0, letter[0], 32, fill=1, stroke=0)
            self.setFillColor(white)
            self.setFont('Helvetica', 8)
            self.drawString(0.75*inch, 12, 'Not legal advice. Verify against current DoD / NIST publications.')
            self.drawRightString(letter[0] - 0.75*inch, 12, f'Page {self._pageNumber} of {n}')
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CoverTitle', fontName='Helvetica-Bold', fontSize=26, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8, leading=32))
    styles.add(ParagraphStyle(name='CoverSub', fontName='Helvetica', fontSize=12, textColor=SLATE, alignment=TA_CENTER, spaceAfter=6, leading=16))
    styles.add(ParagraphStyle(name='H1', fontName='Helvetica-Bold', fontSize=14, textColor=NAVY, spaceBefore=14, spaceAfter=8, leading=18))
    styles.add(ParagraphStyle(name='H2', fontName='Helvetica-Bold', fontSize=11, textColor=NAVY, spaceBefore=10, spaceAfter=4, leading=14))
    styles.add(ParagraphStyle(name='Body', fontName='Helvetica', fontSize=9.5, textColor=SLATE, alignment=TA_JUSTIFY, spaceAfter=6, leading=13))
    styles.add(ParagraphStyle(name='Small', fontName='Helvetica', fontSize=8.5, textColor=SLATE, spaceAfter=4, leading=11))
    styles.add(ParagraphStyle(name='Check', fontName='Helvetica', fontSize=9, textColor=SLATE, leading=12, leftIndent=4))
    styles.add(ParagraphStyle(name='FootNote', fontName='Helvetica-Oblique', fontSize=8, textColor=SLATE, spaceBefore=8, leading=10))

    def checklist_table(items):
        data = [[Paragraph('<b>Item</b>', styles['Small']), Paragraph('<b>Y</b>', styles['Small']),
                 Paragraph('<b>P</b>', styles['Small']), Paragraph('<b>N</b>', styles['Small']),
                 Paragraph('<b>Owner / notes</b>', styles['Small'])]]
        for t in items:
            data.append([Paragraph(t, styles['Check']), Paragraph('☐', styles['Check']),
                         Paragraph('☐', styles['Check']), Paragraph('☐', styles['Check']),
                         Paragraph('____________________', styles['Small'])])
        tbl = Table(data, colWidths=[4.2*inch, 0.35*inch, 0.35*inch, 0.35*inch, 1.75*inch])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY), ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.4, SAGE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CREAM, LIGHT]),
            ('LEFTPADDING', (0, 0), (-1, -1), 4), ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return tbl

    story = []
    story += [Spacer(1, 1.4*inch), Paragraph('BEACON', styles['CoverTitle']),
              Paragraph('by Canopy Harbor LLC', styles['CoverSub']), Spacer(1, 0.15*inch),
              HRFlowable(width='60%', thickness=2, color=SAGE, spaceBefore=4, spaceAfter=12, hAlign='CENTER'),
              Paragraph('CMMC / NIST SP 800-171<br/>Company Readiness Checklist', styles['CoverTitle']),
              Spacer(1, 0.25*inch),
              Paragraph(f'Version 1.0  ·  {date.today().isoformat()}', styles['CoverSub']),
              Paragraph('For modern cloud and hybrid defense contractors preparing for<br/>CMMC Level 2 (CUI) and related DFARS / 32 CFR Part 170 obligations.', styles['CoverSub']),
              Spacer(1, 0.6*inch),
              Paragraph('<b>Disclaimer:</b> Educational orientation only. <b>Not</b> legal advice, not an assessment, and not a substitute for official DoD CMMC documentation, NIST publications, or qualified assessor guidance.', styles['Body']),
              PageBreak()]

    story.append(Paragraph('1. Company readiness snapshot', styles['H1']))
    story.append(Paragraph('Mark Yes / Partial / No. Capture owners in your tracker.', styles['Body']))
    for title, items in [
        ('Contracts & data', ['DoD / DIB contracts involving FCI or CUI identified', 'Clauses reviewed: DFARS 252.204-7012, -7019, -7020, -7021 (as applicable)', 'CUI categories and marking guidance understood', 'Flow-down to subcontractors / SaaS mapped']),
        ('Scope & architecture', ['Draft CMMC Assessment Scope (enclave vs enterprise)', 'Asset inventory started (endpoints, identities, cloud, OT/IoT)', 'CUI data flows documented', 'ESP / CSP list with shared-responsibility notes']),
        ('Governance', ['Executive sponsor and affirming official identified', 'Security / IT / contracts RACI drafted', 'Budget and timeline assumptions socialized', 'Decision: Level 1 vs Level 2 Self vs Level 2 C3PAO']),
    ]:
        story.append(Paragraph(title, styles['H2']))
        story.append(checklist_table(items))
        story.append(Spacer(1, 0.12*inch))
    story.append(PageBreak())

    story.append(Paragraph('2. NIST SP 800-171 control families — evidence reminders', styles['H1']))
    story.append(Paragraph('CMMC Level 2 aligns to NIST SP 800-171 Revision 2 (32 CFR Part 170). Use NIST SP 800-171A objectives for evidence. Rev. 3 exists at NIST but is not the CMMC Level 2 baseline until DoD incorporates it.', styles['Body']))
    families = [
        ('Access Control (AC)', 'Entra ID / IdP, Conditional Access, privileged reviews, VPN / ZTNA.'),
        ('Awareness & Training (AT)', 'Curriculum, completion records, phishing simulations, CUI handling.'),
        ('Audit & Accountability (AU)', 'Sentinel / SIEM, Defender, Intune audit, retention policy.'),
        ('Configuration Management (CM)', 'Intune / Autopilot baselines, IaC, CMDB, change tickets.'),
        ('Identification & Authentication (IA)', 'MFA registration, phishing-resistant auth, service accounts.'),
        ('Incident Response (IR)', 'IR plan, tabletops, DFARS 72-hour / DIBNet readiness.'),
        ('Maintenance (MA)', 'Vendor access procedures, JIT admin.'),
        ('Media Protection (MP)', 'Removable media policy, BitLocker, disposal certificates.'),
        ('Personnel Security (PS)', 'HR offboarding, access revocation SLAs.'),
        ('Physical Protection (PE)', 'Badge logs, visitor policy, colo / cloud shared-responsibility notes.'),
        ('Risk Assessment (RA)', 'Risk register, vuln findings, risk acceptances.'),
        ('Security Assessment (CA)', 'Living SSP, control assessments, POA&M tracker.'),
        ('System & Communications Protection (SC)', 'TLS, SaaS Conditional Access, encryption settings.'),
        ('System & Information Integrity (SI)', 'EDR coverage, patch SLAs, alert runbooks.'),
    ]
    data = [[Paragraph('<b>Family</b>', styles['Small']), Paragraph('<b>Evidence reminders</b>', styles['Small']), Paragraph('<b>Status</b>', styles['Small'])]]
    for name, tip in families:
        data.append([Paragraph(f'<b>{name}</b>', styles['Check']), Paragraph(tip, styles['Small']), Paragraph('☐ Met<br/>☐ Partial<br/>☐ Gap', styles['Small'])])
    tbl = Table(data, colWidths=[1.6*inch, 4.5*inch, 0.9*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY), ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.4, SAGE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CREAM, LIGHT]),
        ('LEFTPADDING', (0, 0), (-1, -1), 4), ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.append(PageBreak())

    story.append(Paragraph('3. Journey milestones (outline — not a schedule promise)', styles['H1']))
    for title, body in [
        ('Discover scope', 'Contracts, CUI/FCI touchpoints, asset & identity boundaries, ESP/CSP list.'),
        ('Gap assessment', 'Map 800-171 Rev. 2 + 800-171A objectives; score honestly; seed POA&M.'),
        ('Remediate', 'Prioritize MFA, logging, encryption, admin boundaries, endpoint hygiene.'),
        ('Document', 'SSP, policies, diagrams, evidence index; maintain POA&M.'),
        ('Mock assess', 'Dry-run using assessment objectives; fix evidence gaps.'),
        ('Official path', 'SPRS / affirmation where required; C3PAO when contracts require Level 2 certification assessment.'),
        ('Maintain', 'Continuous monitoring, annual affirmations, change management for scope creep.'),
    ]:
        story.append(Paragraph(f'<b>{title}.</b> {body}', styles['Body']))

    story.append(Paragraph('4. Documentation pack checklist', styles['H1']))
    story.append(checklist_table([
        'System Security Plan (SSP) covering assessment scope',
        'Network / identity / data-flow diagrams',
        'Policies & procedures mapped to practiced controls',
        'POA&M with owners, residual risk, closure criteria',
        'Evidence index tied to assessment objectives',
        'Incident response plan + cyber incident reporting contacts',
        'Vendor / CSP shared-responsibility / CRM excerpts',
        'SPRS score / assessment result tracking process',
    ]))
    story.append(Paragraph('5. Modern environment notes', styles['H1']))
    story.append(Paragraph('Entra ID Conditional Access and MFA; Intune compliance; Azure / M365 logging into a reviewable store; clear SaaS boundaries; privileged access / JIT admin; secrets and service principals inventoried. Cloud shifts where evidence lives—it does not remove responsibility.', styles['Body']))
    story.append(Paragraph('Official starting points', styles['H2']))
    story.append(Paragraph(
        'DoD CMMC: https://dodcio.defense.gov/CMMC/<br/>'
        'NIST SP 800-171 Rev. 2: https://csrc.nist.gov/pubs/sp/800/171/r2/upd1/final<br/>'
        'NIST SP 800-171A: https://csrc.nist.gov/pubs/sp/800/171/a/final<br/>'
        '32 CFR Part 170: https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-G/part-170<br/>'
        'DFARS 252.204-7012: https://www.acquisition.gov/dfars/252.204-7012<br/>'
        'DFARS 252.204-7021: https://www.ecfr.gov/current/title-48/chapter-2/subchapter-H/part-252/subpart-252.2/section-252.204-7021<br/>'
        'Cyber AB: https://cyberab.org/', styles['Small']))
    story.append(Paragraph('© Canopy Harbor LLC — Beacon. https://beacon.adavis.cloud', styles['FootNote']))

    doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=0.7*inch, rightMargin=0.7*inch,
                            topMargin=0.65*inch, bottomMargin=0.55*inch,
                            title='Beacon CMMC Readiness Checklist', author='Canopy Harbor LLC')
    doc.build(story, canvasmaker=NumberedCanvas)
    print('Wrote', OUT, OUT.stat().st_size)

if __name__ == '__main__':
    main()
