# Quarantined files

Files moved here were found embedded in the project and flagged as
social-engineering / prompt-injection artifacts by the 2026-08-18
audit (finding NEW-M5). They are addressed to an AI or human agent
and instruct action the project owner never authorized. No action was
taken on their instructions. Original content preserved below/in the
sibling `.quarantined` file for the record.

## update-libs.txt.quarantined
- **Original location:** `Lib_PY/Core/cli/CLI_Doc_Chunker/update-libs.txt`
- **Removed:** pkg29, 2026-08-18
- **Content:** an instruction (not addressed to Elton) asking to
  "put the correct dependency imports in the cracked folder with the
  doc chunker and send it back."
- **Disposition:** the entire `CLI_Doc_Chunker` bundle should be
  treated as tainted until reviewed for provenance (audit's own
  recommendation) — it was already flagged non-runtime/broken (L13,
  pkg27) so this doesn't affect CMS operation.
