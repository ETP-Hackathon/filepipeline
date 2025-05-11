# ETP Hackathon: Legal Document Processing Pipeline

## Project Goal

The goal of this hackathon is to develop a robust pipeline that automates the initial processing of a "Klageschrift" (statement of claim) and assists in drafting a "Klageantwort" (statement of defense). This involves extracting key information, leveraging a Large Language Model (LLM) for analysis and argument generation, and producing an editable output document.

The pipeline should be able to:
1.  Ingest a "Klageschrift" document, primarily in scanned PDF format, but also accommodating Word files (.docx).
2.  Extract crucial information from the document's header (e.g., names of parties involved, court details, case number) with 100% accuracy and reliability. The information needs to be structured and usable in code.
3.  Identify and extract individual claims and their supporting arguments from the "Klageschrift".
4.  For each extracted claim, utilize the free Gemini API to:
    *   Analyze the claim and its arguments.
    *   Generate a potential counter-argument. (Note: For this hackathon, the legal correctness of the LLM's output is secondary; the focus is on the integration and process; so even if the response is completely wrong from a legal perspective that does not really matter for the goal of this hackathon).
5.  Compile the generated counter-claims, counter-arguments and supporting documents into a "Klageantwort" Word document.
6.  The output "Klageantwort" must follow a specific structure, as exemplified in the provided `Klageantwort.pdf` (which should be used as a reference for formatting):
    1.  **Headers:** Extracted information such as parties involved, court details, date, case number, etc.
    2.  **Counter-claims:** The specific counter-claims generated.
    3.  **Arguments and Supporting Documents:** The detailed argumentation for each counter-claim, including references to any supporting documents.
7.  Allow users (lawyers) to upload their own empty Word document template. The pipeline should apply the styling (fonts, headings, spacing, etc.) from this template to the generated "Klageantwort", ensuring the output matches the lawyer's preferred formatting.

## Key Technologies & Concepts

*   **Input Formats:** Scanned PDF (primary), DOCX (secondary).
*   **Information Extraction:**
    *   Deterministic extraction for header/metadata (e.g., regex, rule-based parsing).
    *   Extraction of claims and arguments (e.g., NLP techniques, layout analysis).
*   **LLM Integration:** Gemini API for claim analysis and counter-argument generation.
*   **Output Format:** DOCX, styled according to a user-provided template.
*   **Recommended Library:** `python-docx` for Word document manipulation.
*   **Recommended Additional ressources:** google gemini free api access (https://ai.google.dev/gemini-api/docs/pricing), PDF reader for IDE e.g. vscode-pdf for vs code.

## Hackathon Goals & Evaluation Criteria

Your project would be evaluated based on the following (This shall help you better understand the focuse. Don't worry we will not grade you or anything like that.):

### Core Functionality (60%)
1.  **Input Handling (10%):**
    *   Successfully ingests and processes scanned PDF files.
    *   Bonus: Handles `.docx` files as input.
2.  **Deterministic Information Extraction (20%):**
    *   Accuracy and completeness in extracting header information (names, court, case number, etc.). This must be highly reliable.
3.  **Claim & Argument Extraction (15%):**
    *   Effectiveness in identifying and isolating individual claims and their associated arguments from the "Klageschrift".
    *   Robustness to unseen "Klageschriften"
4.  **LLM Integration & Counter-Argument Generation (15%):**
    *   Successful integration with the Gemini API.
    *   Ability to pass extracted claims/arguments to the LLM.
    *   Generation of counter-arguments based on LLM responses for each claim.

### Output & Formatting (30%)
1.  **Structured "Klageantwort" (15%):**
    *   The output Word document correctly includes the extracted header information.
    *   The document follows the specified structure: counterclaims first, then detailed argumentation. **Crucially, the "Klageantwort" must be generated in the exact format provided in the example `Klageantwort.pdf` (but as an editable Word document). Adherence to this specific legal format is a key evaluation criterion, as it directly impacts the efficiency gains for lawyers.**
2.  **Template-Based Styling (15%):**
    *   Successfully uses a user-provided template `.docx` file to apply styling to the generated "Klageantwort".
    *   The output document should reflect the template's formatting. (Demonstrate with a sample template).

### Presentation & Code Quality (10%)
1.  **Clarity of Presentation (5%):**
    *   Clear demonstration of the pipeline's functionality.
    *   Explanation of the approach and challenges.
2.  **Code Readability & Structure (5%):**
    *   Well-organized and understandable codebase.
    *   Use of comments where appropriate.
    *   Please keep in mind that this is something curcial for your upcoming careers and therefore we are happy to see you spend time doing this right.

## Important Considerations

*   **Focus on the Pipeline:** The primary goal is to build a functional end-to-end pipeline. The sophistication of the NLP models for claim extraction or the legal acumen of the LLM's output are secondary for this hackathon.
*   **Modularity:** Design the LLM interaction to be as modular as possible as we will replace this part with out own LLM pipeline later.
*   **Error Handling:** Consider basic error handling for scenarios like unreadable PDFs or API issues.
*   **Future Integration (RAG & FastAPI):** This hackathon project serves as a foundational proof-of-concept. We are concurrently developing a more advanced RAG (Retrieval Augmented Generation) assisted LLM pipeline. The long-term vision is for the claim analysis component of this hackathon project to integrate with that RAG pipeline, which will likely expose its services via a FastAPI endpoint. Therefore, the current interaction with the Gemini API can be considered a placeholder for this future, more sophisticated backend. While you can consider FastAPI for your solution if you wish, it is not a requirement or the main focus for this hackathon; the priority is a functional proof-of-concept for the described document processing workflow.

## Development Environment & Tools

*   We would highly appreciate it if you could mainly use **python as the programming language** for this project.
*   **PDF Viewing:** To inspect the provided PDF files (`Klageschrift.pdf`, `Klageantwort.pdf`), it's highly recommended to have a PDF viewer integrated into your IDE. For VS Code, the **`vscode-pdf`** extension (ID: `tomoki1207.pdf`) works well. You can install it from the Extensions Marketplace.

Thank you for your efforts!

Good luck, and happy hacking!
