# Meshy configuration version 1

The document contains exactly these root fields:

| Field | Meaning |
| --- | --- |
| `version` | Integer `1`. |
| `status` | `draft` or `ready`; only ready configurations resolve. |
| `operation_defaults` | Map from local operation ID to `{ "settings": { ... } }`. |
| `schema_snapshots` | Map from the same operation ID to tool/schema records below. |
| `recipes` | List of named recipe records below. |

Operation IDs are local identifiers, not provider API assumptions. Every ready recipe/default operation needs a snapshot. A ready configuration needs at least one recipe. A draft may contain incomplete production choices, but structural fields and supplied schemas must remain valid. Secret-bearing fields are forbidden recursively; never put credentials in prompt text, values, or schema metadata either. The helper's key checks cannot detect every secret disguised as ordinary prose.

Each snapshot has required `tool` (exact discovered MCP tool name), `captured_at` (record an ISO 8601 timestamp), `input_schema` (captured JSON Schema describing the complete argument object), and `prompt_field` (the tool's actual top-level text-prompt property name, or `null` for operations without one). The schema must be self-contained: `$ref`, `$dynamicRef`, and `$recursiveRef` are rejected to keep validation offline. Preserve constraints when expanding references; do not weaken them to obtain a pass. An explicit `$schema` must identify a dialect recognized by the installed validator; an omitted dialect uses JSON Schema 2020-12. Duplicate JSON keys and non-finite numeric values are rejected.

Each recipe has required `id` (unique nonempty string), `operation`, `criteria` (human-readable selection conditions), `priority` (integer; higher wins), `prompt_template`, `variables` (unique declared variable names), and `settings` (object). Optional `category` is a string and `tags` is a string list. The prompt uses Python string-template syntax `${subject}` or `$subject`; write `$$` for a literal dollar sign. Variable values are strings. Every declared variable must be supplied, even if unused, and extra variables are errors. No variable interpolation occurs inside settings; task-specific image paths and other structured tool arguments belong in `--overrides`.

## Deterministic resolution

```text
validate CONFIG
resolve CONFIG --operation ID
    (--template RECIPE | --match RECIPE [--match RECIPE ...])
    [--variables JSON_OBJECT] [--overrides JSON_OBJECT]
```

Selection considers only explicitly supplied IDs; unknown IDs, operation mismatches, no matches, duplicate matches, and highest-priority ties fail. An explicit named template resolves directly regardless of its priority. The model evaluates criteria before passing match IDs; the helper makes no semantic guesses.

Settings merge by top-level key in this order: operation defaults, selected recipe settings, explicit task overrides. A nested value replaces the prior nested value entirely; there is no deep merge. The rendered prompt is inserted using the snapshot's `prompt_field`; that key cannot also appear in settings. A null prompt field requires an empty prompt. All argument keys must exist in the snapshot's top-level `properties`, and the complete arguments must satisfy the snapshot schema, including required properties, types, enums, and bounds. Defaults annotated in JSON Schema are not auto-filled. Rigging/animation operation or tool names are rejected by the helper; the skill additionally enforces the semantic policy when opaque tool names cannot identify the operation.

Successful `resolve` prints `operation`, `template_id`, `tool`, rendered `prompt`, merged `settings`, complete `arguments`, `schema_captured_at`, `runtime_schema_validation_required: true`, `submission_performed: false`, and `allowance_policy: ".gameflow/AUTOPILOT.md"`. Validation failure exits `2` with a concise error; success exits `0`. Neither command writes files or calls any network/provider tool.

Before submitting, the generation skill must verify the live tool identity and schema and apply the separate allowance ledger. Do not interpret a ready configuration or cached schema pass as spending permission. Do not persist secret values in CLI arguments, shell history, generated output, or task evidence.
