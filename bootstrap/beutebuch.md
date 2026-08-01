# Beutebuch — Harry & Marv

Jeder Fund des Read-Only Red Teams landet hier (Beutezug-Dreisatz, siehe
[CLAUDE.md](../CLAUDE.md)). Finder ≠ Fixer: Übergabe an Frank.

**Status-Kette**: `offen` → `an Frank übergeben` → (bei Scheitern)
`an Axel übergeben` → `Fix-Plan liegt vor` → `erledigt (Frank-Fix, <commit>)`

## Vorlage

```markdown
### HM-<Nr> — <Kurztitel>
- **Angreifer**: Harry | Marv
- **Schweregrad**: kritisch | hoch | mittel | klein
- **Status**: offen
- **Reproschritte**:
  1. …
- **Erwartung**: …
- **Realität**: …
- **Reproducer-Test**: {{TEST_ORDNER}}test_hm<nr>_<stichwort> (optional)
```

> Diesen Vorlage-Block **nicht löschen**. Harry und Marv richten ihre Funde
> daran aus; ohne ihn divergieren die Formate ab dem zweiten Sweep und die
> Zustandsmaschine findet die Status-Zeilen nicht mehr.

## Funde
