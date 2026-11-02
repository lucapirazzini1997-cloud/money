#!/usr/bin/env python3
"""Hook PreToolUse: blocca le azioni che le regole del progetto vietano.

- Edit/Write sui moduli di versioni gia' consegnate (versione con SHA in build.py) e sui pezzi congelati
  (storico_054/, pezzo_055/, basi/).
- git add forzato o commit con ROM (*.gba): il repository e' pubblico.
- pkill -f / killall: in questo container uccidono anche la shell di Claude.
Uscita 2 = azione bloccata, il motivo va a Claude su stderr.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def blocca(motivo):
    print('BLOCCATO dalla guardia del progetto: ' + motivo, file=sys.stderr)
    sys.exit(2)


def consegnate():
    t = (ROOT / 'build.py').read_text(encoding='utf-8')
    sha = t[t.index('SHA = {'):t.index('}', t.index('SHA = {'))]
    con_sha = set(re.findall(r"'(\d{3})'\s*:\s*'[0-9a-f]{64}'", sha))
    return {mod for ver, mod in re.findall(r"\('(\d{3})',\s*'(v\d{3}_\w+)'\)", t) if ver in con_sha}


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return
    tool, inp = ev.get('tool_name', ''), ev.get('tool_input') or {}
    if tool in ('Edit', 'Write', 'MultiEdit', 'NotebookEdit'):
        p = Path(inp.get('file_path') or inp.get('notebook_path') or '')
        try:
            rel = p.resolve().relative_to(ROOT)
        except ValueError:
            return
        parti = rel.parts
        if parti and parti[0] in ('storico_054', 'pezzo_055', 'basi'):
            blocca('%s fa parte della catena congelata (0.54/0.55 o ROM di base): non si modifica.' % rel)
        if len(parti) == 2 and parti[0] == 'versioni' and p.stem in consegnate():
            blocca('versioni/%s appartiene a una versione gia\' consegnata (SHA in build.py). '
                   'Le correzioni vanno in un modulo nuovo della prossima versione.' % p.name)
    elif tool == 'Bash':
        cmd = inp.get('command', '')
        # il testo dentro gli here-document e' contenuto di file, non comandi
        cmd = re.sub(r"<<-?\s*(['\"]?)(\w+)\1.*?^\s*\2\s*$", '', cmd, flags=re.S | re.M)
        # ... e cosi' il testo fra virgolette (messaggi di commit, echo)
        cmd = re.sub(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"", '""', cmd, flags=re.S)
        CMD = r'(?:^|[;&|(\n]|\$\()\s*(?:sudo\s+)?'
        if re.search(CMD + r'(?:pkill\s+(?:-\w+\s+)*-f\b|killall\b)', cmd, re.M):
            blocca('pkill -f / killall uccidono anche la shell di Claude. Usa: ps aux | grep ... | awk ... | xargs kill')
        if re.search(CMD + r'git\s+add\b[^;&|\n]*(?:\s-f\b|--force)[^;&|\n]*\.gba', cmd, re.M):
            blocca('aggiunta forzata di una ROM: il repository e\' pubblico, le ROM si consegnano come file.')
        if re.search(CMD + r'git\s+(?:commit|push)\b', cmd, re.M):
            r = subprocess.run(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, capture_output=True, text=True)
            rom = [f for f in r.stdout.split() if f.lower().endswith('.gba')]
            if rom:
                blocca('ROM nel commit (%s): toglile con git rm --cached.' % ', '.join(rom))


if __name__ == '__main__':
    main()
