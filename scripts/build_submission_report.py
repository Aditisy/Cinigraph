"""Build the Exercise 3 report in the supplied lab-report section order."""
from pathlib import Path
from xml.sax.saxutils import escape
import json
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                              PageBreak, Preformatted, Image, HRFlowable)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'pdf'
OUT.mkdir(parents=True,exist_ok=True)
TARGET=OUT/'1GA23AI003_Exp3_Movie_Graph_RAG.pdf'
DATE='7 October 2026'
BLUE=colors.HexColor('#225586')
PALE=colors.HexColor('#dce8f3')
GRAY=colors.HexColor('#777777')
WIDTH=A4[0]-96
styles={
    'body':ParagraphStyle('body',fontName='Times-Roman',fontSize=11,leading=14,spaceAfter=7,allowWidows=0,allowOrphans=0),
    'small':ParagraphStyle('small',fontName='Times-Roman',fontSize=10,leading=12,spaceAfter=5),
    'heading':ParagraphStyle('heading',fontName='Times-Bold',fontSize=14,leading=17,textColor=BLUE,spaceBefore=12,spaceAfter=5,keepWithNext=True),
    'sub':ParagraphStyle('sub',fontName='Times-Bold',fontSize=11.5,leading=14,textColor=BLUE,spaceBefore=7,spaceAfter=5,keepWithNext=True),
    'title':ParagraphStyle('title',fontName='Times-Bold',fontSize=16,leading=20,textColor=BLUE,alignment=1,spaceAfter=9),
    'code':ParagraphStyle('code',fontName='Courier',fontSize=8.5,leading=11,backColor=colors.HexColor('#f1f1f1'),borderPadding=8,spaceBefore=5,spaceAfter=10),
}
story=[]
md=['# LAB EXERCISE: 3','',f'Aditi S Yaranal | 1GA23AI003 | 7th Semester | AIML | Global Academy of Technology | {DATE}','']
def p(text,kind='body'):
    story.append(Paragraph(escape(text).replace('\n','<br/>'),styles[kind]))
    md.append(text+'\n')
def h(text):
    story.append(Paragraph(escape(text),styles['heading']))
    story.append(HRFlowable(width='100%',thickness=.7,color=BLUE,spaceAfter=7))
    md.append('## '+text+'\n')
def sub(text):p(text,'sub')
def bullet(text):
    story.append(Paragraph(escape(text),ParagraphStyle('bullet',parent=styles['body'],leftIndent=12,firstLineIndent=-8),bulletText='\u2022'))
    md.append('- '+text+'\n')
def table(rows,widths,header=True):
    cells=[[Paragraph(escape(str(c)).replace('\n','<br/>'),styles['small']) for c in row] for row in rows]
    t=Table(cells,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    commands=[('GRID',(0,0),(-1,-1),.45,colors.HexColor('#adb4ba')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]
    if header:commands += [('BACKGROUND',(0,0),(-1,0),PALE)]
    t.setStyle(TableStyle(commands));story.append(t);story.append(Spacer(1,9))
    md.extend([' | '.join(str(c).replace('\n',' ') for c in row) for row in rows]);md.append('')
def code(text):
    block=Table([[Preformatted(text,styles['code'])]],colWidths=[WIDTH],hAlign='LEFT')
    block.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f1f1f1')),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(block);story.append(Spacer(1,9));md.extend(['```python',text,'```',''])
def page():story.append(PageBreak())
def diagram(labels):
    d=Drawing(WIDTH,66)
    bw=(WIDTH-36)/3
    for i,label in enumerate(labels):
        x=i*(bw+18)
        d.add(Rect(x,10,bw,48,fillColor=PALE,strokeColor=BLUE,strokeWidth=.6))
        for j,line in enumerate(label.split('\n')):
            d.add(String(x+bw/2,40-j*13,line,fontName='Times-Roman',fontSize=10,textAnchor='middle'))
        if i<2:
            d.add(Line(x+bw,34,x+bw+16,34,strokeColor=BLUE))
            d.add(Polygon([x+bw+16,34,x+bw+11,37,x+bw+11,31],fillColor=BLUE,strokeColor=BLUE))
    story.append(d)

# Page 1: student details and the first three template sections.
p('LAB EXERCISE: 3','title')
p('CineGraph: Movie Question Answering using Graph RAG','title')
table([['Student Name','Aditi S Yaranal','USN','1GA23AI003'],['Semester / Department','7th Semester / AIML','Date',DATE],['Institution','Global Academy of Technology','Course','AML23702']], [105,195,45,WIDTH-345],False)
h('Aim / Objective')
p('To design and implement a small retrieval-augmented generation application that uses the Neo4j Movies dataset as its knowledge graph, retrieves movie, actor and director information through Cypher queries, and uses a local LLM to generate natural-language answers.')
h('Expected Outcomes Addressed')
for s in [
    'Load and use the Neo4j movie graph: the local database contains 38 movies, 133 people and 253 relationships.',
    'Convert user questions into graph queries: a rule-based intent parser selects one of six parameterized Cypher templates.',
    'Retrieve relevant movie and actor data: cast, directors, filmographies and release details are returned as evidence rows.',
    'Generate grounded answers: Qwen receives graph evidence; the interface exposes sources and flags missing or invalid citation IDs. Semantic grounding remains imperfect.',
    'Support movie QA and recommendations: the web application answers supported questions and ranks related movies by shared actors.'
]:bullet(s)
h('Tools & Technologies Used')
table([['Category','Tool / Library','Version','Purpose'],['Language','Python','3.12.14','Backend and evaluation'],['Graph database','Neo4j Community','2026.09.0','Movies graph and Cypher'],['Database driver','neo4j Python driver','6.4.0','Parameterized retrieval'],['Web framework','Flask','3.1.3','Local web API'],['LLM / inference','Qwen2.5 3B Instruct / llama.cpp','Q4_K_M / b11443','Local answer generation'],['Frontend','HTML, CSS, JavaScript, SVG','Web standards','Responsive UI and graph']], [85,155,90,WIDTH-330])

# Page 2.
page();h('Dataset / Corpus Description')
p('Source: the official neo4j-graph-examples/movies repository. The import script is included as data/movies.cypher. Its source and SHA-256 are recorded in data/provenance.json. It is loaded into a dedicated local Neo4j instance; the initialization script imports only when no Movie nodes are present.')
table([['Data element','Description / measured count'],['Movie nodes','38; properties: title, released, tagline'],['Person nodes','133; properties: name, born'],['Relationships','253 total, including ACTED_IN, DIRECTED, WROTE, PRODUCED, REVIEWED and FOLLOWS'],['Relationships queried','ACTED_IN (with roles) and DIRECTED'],['Matching / constraints','Case-insensitive exact names; official title and person-name uniqueness constraints']], [145,WIDTH-145])
p('Sample record: Movie {title: "The Matrix", released: 1999, tagline: "Welcome to the Real World"}. Sample relation: (Keanu Reeves)-[ACTED_IN {roles: ["Neo"]}]->(The Matrix).')
p('The corpus is an educational sample, not a complete film catalogue. For example, it includes Emil Eifrem in The Matrix cast. Grounding means fidelity to the supplied graph, not independent verification of real-world film facts.')
h('System Architecture / Pipeline Design')
diagram(['User question\nWeb interface','Intent + entity\nTemplate selection','Neo4j\nCypher retrieval'])
diagram(['Evidence rows\nR1, R2, ...','Local Qwen LLM\nAnswer generation','Answer + evidence\nQuery inspection'])
for s in [
    'Module 1 - Input handling: validate an English question of up to 500 characters and identify the movie/person.',
    'Module 2 - Retrieval: bind the entity to a fixed read-only query and retrieve bounded rows through the Neo4j driver.',
    'Module 3 - Evidence preparation: assign row IDs; detect partial results by fetching one extra row.',
    'Module 4 - Generation: send facts to the local model. Empty results skip generation; model failures preserve evidence.',
    'Module 5 - Presentation: show answers, source rows, Cypher, movie search and the relationship graph.'
]:bullet(s)
p('Core schema: (Person)-[ACTED_IN {roles}]->(Movie); (Person)-[DIRECTED]->(Movie). The LLM does not write or execute Cypher.')

# Page 3.
page();h('Backend Implementation')
sub('6.1 Approach / Algorithm')
p('The parser recognizes cast, director, actor_movies, director_movies, movie and recommend intents. It uses case-insensitive patterns and exact entity matching. Unsupported phrasing returns examples instead of guessing. Query values are parameterized, so user text cannot change the query structure.')
p('For recommendations, traverse from the seed movie to shared actors and then to other movies. Exclude the seed, count distinct shared actors and sort by descending count, with title breaking ties. This score measures cast overlap, not popularity or user preference.')
sub('6.2 Key Code Snippets')
p('1. Question parsing and template selection','small')
code('for intent, pattern in PATTERNS:\n    match = re.fullmatch(pattern, q, flags=re.IGNORECASE)\n    if match:\n        entity = match.group(1).strip().strip(\'"\').strip()\n        if entity:\n            return intent, entity')
p('2. Read-only parameterized graph retrieval','small')
code('records, _, _ = driver.execute_query(\n    QUERIES[intent],\n    parameters_={"entity": entity, "limit": limit + 1},\n    database_=database, routing_="r")\nrows = [record.data() for record in records]\nreturn rows[:limit], len(rows) > limit')
p('3. Local model request (excerpt; configuration supplies the endpoint)','small')
code('payload = {\n    "messages": [\n        {"role": "system", "content": local_system},\n        {"role": "user",\n         "content": "Question: " + question + "\\nFacts:\\n" + facts}\n    ],\n    "max_tokens": 650, "temperature": 0, "stream": False\n}\n# POST payload to llama.cpp /v1/chat/completions')
p('The application checks whether generated citation IDs exist in the evidence range. This check does not prove that each cited row supports the claim. A visible warning is shown when citations are missing or misnumbered.')

# Page 4.
page();h('Frontend / UI Implementation')
sub('7.1 Framework Choice')
p('Flask serves the local API and static HTML/CSS/JavaScript frontend. SVG renders the movie relationship graph. The interface is responsive and was checked at desktop and 390-pixel mobile widths.')
sub('7.2 Interface Features')
for s in ['Ask CineGraph: typed questions, sample prompts, generated answers, elapsed time, evidence tables and Cypher.',
          'Movie collection: search 38 titles and select a movie to ask about it.',
          'Knowledge graph: choose a movie to display its cast and directors.',
          'About the project: architecture, limitations and a link to the report.']:
    bullet(s)
image=ROOT/'output'/'CineGraph_Report_Screenshot.jpg'
if image.exists():
    from PIL import Image as PILImage
    iw,ih=PILImage.open(image).size
    story.append(Image(str(image),width=WIDTH,height=WIDTH*ih/iw))
    p('Figure 1. Working frontend: a live director answer with its graph evidence (captured '+DATE+').','small')
p('Run locally at http://127.0.0.1:8765. Double-click Launch CineGraph.cmd to restart the database, model and web server. No paid LLM API key is required.')

# Page 5.
page();h('Sample Input & Output')
table([['Input','Component','Observed output'],
['Who directed The Matrix?','director','The Matrix was directed by Lana Wachowski [R1] and Lilly Wachowski [R2].'],
['When was The Matrix released?','movie','The Matrix was released in 1999. [R1]'],
['Movies with Tom Hanks','actor_movies','Ten movie rows including Apollo 13 (1995); partial-list notice displayed.'],
['Recommend movies like The Matrix','recommend','Eight retrieved candidate movies; shared actor counts and names available as evidence.'],
['Tell me about __missing_movie__','No evidence','No matching evidence found; LLM not called.'],
['Who won an Oscar?','Unsupported input','HTTP 400 with supported question examples.']], [155,90,WIDTH-245])
h('Results (Deliverable-Specific Outputs)')
sub('Neo4j Database Instance')
p('Local Neo4j Community is configured at bolt://127.0.0.1:7689; its Browser interface is at http://127.0.0.1:7479. The loaded graph has 171 nodes and 253 relationships. Credentials are private and excluded from the repository.')
sub('Cypher Query Templates')
p('Six complete templates are included in queries.json and cypher_templates.cypher. All application templates are read-only and use bound parameters.')
sub('Retrieved Recommendation Evidence')
table([['Movie','Year','Shared actors / score'],['The Matrix Reloaded','2003','Hugo Weaving, Laurence Fishburne, Carrie-Anne Moss, Keanu Reeves / 4'],['The Matrix Revolutions','2003','Hugo Weaving, Laurence Fishburne, Carrie-Anne Moss, Keanu Reeves / 4'],['Cloud Atlas','2012','Hugo Weaving / 1']], [145,45,WIDTH-190])
p('Other deliverables: a working web/CLI prototype, setup and launch scripts, this report, offline_test_results.txt and output/live_results.json with actual questions, answers, source rows, parameters and timings.')

# Page 6.
page();h('Evaluation / Analysis')
sub('Performance Evaluation')
results=json.loads((ROOT/'output/live_results.json').read_text(encoding='utf-8'))
times=[r['elapsed_seconds'] for r in results if r.get('evidence')]
table([['Check','Observed result','Interpretation'],['Unit / web tests','12 / 12 passed','Parser, parameters, errors, payloads, routing and PDF endpoint'],['Live Neo4j checks','7 / 7 passed','Six retrieval intents plus absent entity'],['Live website acceptance','8 / 8 passed','Expected retrieval and request behavior; successful model calls'],['Evidence-backed latency',f'{min(times):.2f}-{max(times):.2f} s; mean {sum(times)/len(times):.2f} s','Six requests in one local run, not a benchmark'],['Semantic groundedness','Not scored quantitatively','Known citation omissions and unsupported commentary remain']], [135,130,WIDTH-265])
sub('Interpretation')
p('Passing retrieval tests does not establish perfect answer quality. The saved cast answer omitted citations, and the Nora Ephron answer added genre/style commentary absent from the retrieved rows. The interface warns about missing citations; human checking is still needed for semantic correctness. No precision, recall or F1 score is invented.')
h('Challenges Faced & Solutions')
bullet('Java runtime conflict: Neo4j initially selected a stripped Android runtime without the required vector module. The launcher now resolves the full installed JDK for the project.')
bullet('Weak model adherence: the initial 1.5B model produced poor citations and vague recommendations. A local 3B model and simpler evidence prompts improved readability; the report retains observed limitations.')
bullet('Incomplete or unsupported questions: exact matching can return no data. Explicit error messages and example question forms guide the user; empty evidence prevents an LLM call.')
bullet('Private runtime management: credentials and large model/database files are stored under .runtime and excluded from Git. Reproduction scripts download the required runtimes.')
h('Conclusion')
p('CineGraph implements a small graph RAG application with a real Neo4j Movies backend, controlled Cypher retrieval, local LLM generation and an inspectable web interface. The exercise demonstrates graph modelling, intent-based retrieval and evidence-grounded prompting. Future improvements include alias resolution, semantic citation verification and a larger held-out question set.')

# Page 7.
page();h('Project Repository (GitHub Link)')
table([['Field','Submission details'],['GitHub Repository URL','https://github.com/Aditisy/Cinigraph'],['Repository Visibility','Public'],['Branch Used for Submission','main'],['Student / USN','Aditi S Yaranal / 1GA23AI003'],['Date of Submission',DATE]], [155,WIDTH-155])
p('The repository contains backend/frontend source, the official data import script, six Cypher templates, configuration examples, requirements, setup/run instructions, test evidence and the final report. Private credentials, local database files and model/runtime binaries are excluded. They can be recreated with the included setup scripts.')
sub('Reproduction Commands')
code('py -m venv .venv\n.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n.\\.venv\\Scripts\\python.exe setup_local.py\nCopy-Item config.local.example.json config.json\npowershell -ExecutionPolicy Bypass -File .\\start_local.ps1')
p('Prerequisites: Windows, Python 3.10 or later, a supported full Java 21/25 JDK and sufficient disk space for runtime/model downloads. The Flask server is for local review; the GitHub repository itself does not host the running Neo4j/LLM application.')
h('References')
for s in [
    'Lab Exercise with Rubrics (2).pdf: Exercise 3 on page 2 and assessment rubric on pages 4-5.',
    'ANLP_Lab1_report013.pdf: user-provided report-format reference; section order and evaluation-sheet styling adapted for Exercise 3.',
    'Neo4j Movies dataset: https://github.com/neo4j-graph-examples/movies',
    'Neo4j Python driver: https://neo4j.com/docs/python-manual/current/query-simple/',
    'Neo4j Windows installation: https://neo4j.com/docs/operations-manual/current/installation/windows/',
    'llama.cpp runtime: https://github.com/ggml-org/llama.cpp',
    'Qwen model: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF',
    'Flask documentation: https://flask.palletsprojects.com/'
]:bullet(s)

# Page 8: faculty evaluation sheet, intentionally ungraded.
page();story.append(Spacer(1,22))
p('ADVANCE NLP (AML23702)','title')
p('LAB EXERCISE EVALUATION SHEET','title')
table([['Student Name','Aditi S Yaranal'],['USN','1GA23AI003'],['Lab Exercise No.','3'],['Experiment Title','CineGraph: Movie Question Answering using Graph RAG'],['Semester / Department','7th Semester / AIML'],['Institution','Global Academy of Technology']], [145,WIDTH-145],False)
p('Marks Awarded','title')
criteria=[('Problem Understanding & Scope','5'),('Pipeline Design & Methodology','10'),('Implementation Correctness','10'),('Use of NLP Tools / Models','5'),('Output Quality / Task Performance','10'),('Analysis & Interpretation','5'),('Documentation & Deliverables','2.5'),('Presentation & Reproducibility','2.5')]
table([['Sl. No.','Evaluation Criteria','Max Marks','Marks Obtained']]+[[str(i),c,m,''] for i,(c,m) in enumerate(criteria,1)]+[['','Total','50','']], [40,WIDTH-175,60,75])
sub('Overall Comments')
story.append(Table([[''],[''],['']],colWidths=[WIDTH],rowHeights=[22,22,22],style=TableStyle([('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#bbbbbb'))])))
story.append(Spacer(1,22))
table([['Date of Submission',DATE],['Signature of Faculty','']], [145,WIDTH-145],False)

class NumberedCanvas(canvas.Canvas):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pages=[]
    def showPage(self):self.pages.append(dict(self.__dict__));self._startPage()
    def save(self):
        total=len(self.pages)
        for state in self.pages:
            self.__dict__.update(state)
            self.setFont('Times-Italic',8);self.setFillColor(GRAY)
            self.drawString(48,A4[1]-31,'Department of AIML')
            self.drawRightString(A4[0]-48,A4[1]-31,'Advance NLP (AML23702)')
            self.setStrokeColor(colors.HexColor('#b6b6b6'));self.setLineWidth(.4)
            self.line(48,A4[1]-38,A4[0]-48,A4[1]-38)
            self.setFont('Times-Roman',8)
            self.drawCentredString(A4[0]/2,25,f'Page {self._pageNumber} of {total}')
            super().showPage()
        super().save()

SimpleDocTemplate(str(TARGET),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=54,bottomMargin=42,
                  title='1GA23AI003 - Exercise 3 - CineGraph',author='Aditi S Yaranal').build(story,canvasmaker=NumberedCanvas)
shutil.copyfile(TARGET,OUT/'Exercise_3_Report.pdf')
(ROOT/'REPORT.md').write_text('\n'.join(md),encoding='utf-8')
print(TARGET)
