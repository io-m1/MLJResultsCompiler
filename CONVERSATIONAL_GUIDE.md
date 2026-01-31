# Conversational Guide for MLJ Results Compiler

This guide demonstrates how to interact with the MLJ Results Compiler bot using natural language.

## Overview

The bot now understands natural language and can detect your intent without requiring specific commands. Just tell it what you want to do!

## Supported Intents

### 1. Test Consolidation (Active)

**What it does:** Merges multiple test Excel files by matching participant emails.

**Example phrases:**
- "I want to consolidate test results"
- "Help me merge test files"
- "Combine my Excel test sheets"
- "Consolidate scores from multiple tests"
- "Merge test 1, 2, and 3"

**Conversation flow:**
```
User: I need to consolidate test results
Bot: 📊 Test Consolidation Mode
     I'll help you consolidate test results!
     
     📤 Send me your Excel files:
     • Test 1.xlsx
     • Test 2.xlsx
     • Test 3.xlsx (and so on)
     
     I'll merge them by participant email.

[User uploads Test 1.xlsx]

Bot: ✅ Test 1 received
     📊 Test Consolidation in Progress
     
     ✅ You've uploaded 1 file(s)
     
     You can:
     • Upload more test files
     • Use /consolidate to process now

[User uploads Test 2.xlsx]

Bot: ✅ Test 2 received
     [Ready to consolidate]

User: /consolidate

Bot: [Processes files and returns consolidated results]
```

### 2. Invoice Processing (Coming Soon)

**What it does:** Extracts invoice data from PDFs and images, generates summaries.

**Example phrases:**
- "Process my invoices"
- "Extract invoice data"
- "Sum up my billing records"
- "Generate invoice summary"

**Current response:**
```
User: I need to process invoices
Bot: 💰 Invoice Processing
     This feature is coming soon! Currently, I specialize in test result consolidation.
     
     📤 Send me test Excel files to get started.
```

### 3. Image Text Extraction (Coming Soon)

**What it does:** Uses OCR to extract text and tables from images.

**Example phrases:**
- "Extract text from this image"
- "Read this photo"
- "OCR this scan"
- "Get text from image"

**Required:** pytesseract package

### 4. Table Merging (Coming Soon)

**What it does:** Intelligently merges any tabular data files.

**Example phrases:**
- "Merge these tables"
- "Combine my data files"
- "Join these spreadsheets"
- "Consolidate these CSV files"

### 5. Data Cleaning (Coming Soon)

**What it does:** Cleans and standardizes data formats.

**Example phrases:**
- "Clean my data"
- "Fix formatting issues"
- "Standardize this file"
- "Normalize the data"

### 6. Report Generation (Coming Soon)

**What it does:** Creates formatted reports from data.

**Example phrases:**
- "Create a report"
- "Generate summary"
- "Make a PDF report"
- "Produce a document"

## Conversation Examples

### Example 1: First-time user

```
User: Hi
Bot: I'm here to help! 🤖
     
     I can help with:
     • Test result consolidation 📊
     • Merging Excel files by email
     • Creating color-coded reports
     
     Just upload your test files to get started!

User: I have 3 test files to merge
Bot: 📊 Test Consolidation Mode
     I'll help you consolidate test results!
     
     📤 Send me your Excel files:
     • Test 1.xlsx
     • Test 2.xlsx  
     • Test 3.xlsx (and so on)
     
     I'll merge them by participant email.

[User uploads files and processes them]
```

### Example 2: Experienced user

```
User: merge tests
Bot: 📊 Test Consolidation Mode
     [Instructions...]

[User uploads Test_1.xlsx, Test_2.xlsx, Test_3.xlsx]

User: /consolidate
Bot: [Processes files]
     ✅ Consolidated 3 test files
     📊 25 participants found
     [Sends consolidated file]
```

### Example 3: Exploring features

```
User: what can you do?
Bot: I'm here to help! 🤖
     
     I can help with:
     • Test result consolidation
     • Invoice processing
     • Text extraction from images
     • Merging tables
     • Generating reports
     • Data cleaning
     
     What would you like to do?

User: show me an example of test consolidation
Bot: 📊 Test Consolidation Mode
     I'll help you consolidate test results!
     [etc...]
```

## Traditional Command Interface

The bot still supports traditional commands for users who prefer them:

- `/start` - Show welcome message
- `/help` - Show help information
- `/consolidate` - Process uploaded files
- `/cancel` - Cancel current operation

## Tips for Best Results

1. **Be specific but natural**: "I want to merge my test Excel files" works better than just "merge"

2. **Use keywords**: Mention key concepts like "test", "consolidate", "merge", "Excel"

3. **Follow the flow**: The bot will guide you through the process - follow its suggestions

4. **Upload files when prompted**: After expressing your intent, upload the relevant files

5. **Use /consolidate when ready**: Once you've uploaded all files, use `/consolidate` to process

## Intent Detection

The bot uses an intelligent intent detection system that:

- Analyzes your message for keywords
- Matches against known patterns
- Calculates confidence scores
- Selects the best matching intent
- Provides contextual responses

**Confidence threshold:** 70% (adjustable in config)

If the bot is unsure about your intent (confidence < 70%), it will:
- Provide suggestions
- List available capabilities
- Ask clarifying questions

## Context Awareness

The bot maintains conversation context:
- Remembers what you've said
- Tracks uploaded files
- Understands follow-up questions
- Provides relevant suggestions based on current state

**Example:**
```
User: I need to consolidate tests
Bot: [Explains test consolidation]

[User uploads file]

User: can I add more?
Bot: [Understands context - knows you're asking about adding more test files]
     Yes! Upload more test files or use /consolidate to process now.
```

## Multi-Format Support

While test consolidation (Excel) is fully functional, the bot is designed to handle:

- **Spreadsheets**: .xlsx, .xls, .csv, .tsv
- **Documents**: .pdf, .docx, .txt
- **Images**: .jpg, .png, .jpeg, .bmp, .tiff
- **Data files**: .json, .xml, .yaml

*Note: Advanced format support requires optional dependencies (see requirements.txt)*

## Future Enhancements

Upcoming features:
- ✅ Natural language understanding (implemented)
- ✅ Intent detection (implemented)
- ✅ Multi-turn conversations (implemented)
- ⏳ OCR for images (requires pytesseract)
- ⏳ PDF text extraction (requires pdfplumber)
- ⏳ Invoice processing agent
- ⏳ Generic table merger
- ⏳ Data cleaning tools
- ⏳ Report generator

## Troubleshooting

**Bot doesn't understand my request:**
- Try rephrasing with clearer keywords
- Use specific terms like "test", "consolidate", "merge"
- Check examples in this guide

**Feature not available:**
- Some features are planned but not yet implemented
- The bot will inform you when a feature is coming soon
- Use test consolidation for immediate needs

**Need help:**
- Use `/help` command
- Ask "what can you do?"
- Consult this guide

## Feedback

The conversational interface is designed to be intuitive and helpful. If you have suggestions or encounter issues, please provide feedback to help improve the system.
