What:

- help anca automated the monthly status report(MSR) for client.

Impact:

- 3 hours each, 7 of them -> 21 hours a month.
- If it poorly writen, it would take longer.
- Also complication when the manger make error.

Why

- save time for many managers! - high impact
- reduce human error
- increase efficiency
- increase accuracy

How:

Use LLM and software build a tool with a UI:

- input: data word files from individual staffs.
- output: well-formatted MSR file for each department/project.
- process:
- read data from word files
- 
- extract data for output file:
- MSR number: "Monthly Status Report # 52" first line
- Task order number: "HQ0034-20-F-0208 " second line
- Task order: "Federal Facilities Division (FFD)" third line
- staff name: first 2 words in the file name
- What did they do: always under "work performed during month year"

Formatting:

- Should keep the exact content. Only correct grammar and complete sentences.
