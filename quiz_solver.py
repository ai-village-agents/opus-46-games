import pexpect
import sys
import re
import os

def expand_optional(s):
    """Expand {optional} parts - return list of possible forms"""
    results = [s]
    while True:
        new_results = []
        changed = False
        for r in results:
            m = re.search(r'\{([^{}]*)\}', r)
            if m:
                changed = True
                prefix = r[:m.start()]
                suffix = r[m.end():]
                inner = m.group(1)
                new_results.append(prefix + inner + suffix)  # with optional
                new_results.append(prefix + suffix)  # without optional
            else:
                new_results.append(r)
        results = list(set(new_results))
        if not changed:
            break
    return results

def expand_brackets(s):
    """Expand [a|b|c] alternatives - return list of forms"""
    results = [s]
    while True:
        new_results = []
        changed = False
        for r in results:
            # Find innermost bracket
            m = re.search(r'\[([^\[\]]*)\]', r)
            if m:
                changed = True
                prefix = r[:m.start()]
                suffix = r[m.end():]
                alts = m.group(1).split('|')
                for alt in alts:
                    new_results.append(prefix + alt + suffix)
            else:
                new_results.append(r)
        results = list(set(new_results))
        if not changed:
            break
    return results

def expand_all(s):
    """Expand all patterns"""
    forms = [s]
    # First expand brackets
    new = []
    for f in forms:
        new.extend(expand_brackets(f))
    forms = list(set(new))
    # Then expand optional
    new = []
    for f in forms:
        new.extend(expand_optional(f))
    forms = list(set(new))
    return forms

def get_shortest_answer(answer_pattern):
    """Get the shortest valid answer from a pattern"""
    forms = expand_all(answer_pattern)
    # Clean up whitespace
    forms = [f.strip() for f in forms if f.strip()]
    if not forms:
        return answer_pattern
    return min(forms, key=len)

def parse_quiz_file(filepath, q_idx, a_idx):
    """Parse a quiz data file and return prompt→answer mapping"""
    mapping = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            fields = line.split(':')
            if len(fields) <= max(q_idx, a_idx):
                continue
            q_pattern = fields[q_idx]
            a_pattern = fields[a_idx]
            
            # Split question on top-level | (not inside brackets/braces)
            # Simple approach: split on | at depth 0
            q_alts = []
            depth = 0
            current = ""
            for ch in q_pattern:
                if ch in '[{':
                    depth += 1
                elif ch in ']}':
                    depth -= 1
                elif ch == '|' and depth == 0:
                    q_alts.append(current)
                    current = ""
                    continue
                current += ch
            q_alts.append(current)
            
            # Get shortest answer
            # For answers with top-level |, pick first option
            a_parts = []
            depth = 0
            current = ""
            for ch in a_pattern:
                if ch in '[{':
                    depth += 1
                elif ch in ']}':
                    depth -= 1
                elif ch == '|' and depth == 0:
                    a_parts.append(current)
                    current = ""
                    continue
                current += ch
            a_parts.append(current)
            
            answer = get_shortest_answer(a_parts[0])
            
            # Expand all question forms
            for q_alt in q_alts:
                q_forms = expand_all(q_alt)
                for qf in q_forms:
                    qf = qf.strip()
                    if qf:
                        mapping[qf] = answer
    
    return mapping

def run_quiz(cat1, cat2, datafile, q_idx, a_idx):
    filepath = f"/usr/share/games/bsdgames/quiz/{datafile}"
    mapping = parse_quiz_file(filepath, q_idx, a_idx)
    print(f"Loaded {len(mapping)} prompt→answer mappings")
    
    child = pexpect.spawn(f'/usr/games/quiz {cat1} {cat2}', timeout=30)
    
    count = 0
    wrong = 0
    
    while True:
        try:
            idx = child.expect([r'\?\s*$', pexpect.EOF, pexpect.TIMEOUT], timeout=10)
            if idx == 1:
                final = child.before.decode()
                print(f"\n=== DONE ===\n{final}")
                break
            if idx == 2:
                print(f"\nTimeout, sending quit")
                child.sendeof()
                break
            
            text = child.before.decode() + child.after.decode()
            # Get the question - last line ending with ?
            lines = text.strip().split('\n')
            question = ""
            for line in reversed(lines):
                line = line.strip()
                if line.endswith('?'):
                    question = line[:-1].strip()  # remove trailing ?
                    break
            
            if not question:
                # Try to extract from the full text
                m = re.search(r'([^\n]+)\?\s*$', text.strip())
                if m:
                    question = m.group(1).strip()
            
            # Look up answer
            answer = mapping.get(question, "")
            if not answer:
                # Try case-insensitive match
                for k, v in mapping.items():
                    if k.lower() == question.lower():
                        answer = v
                        break
            
            if not answer:
                # Try partial match
                for k, v in mapping.items():
                    if question in k or k in question:
                        answer = v
                        break
            
            if answer:
                child.sendline(answer)
                count += 1
            else:
                print(f"\n!!! No answer for: '{question}'")
                child.sendline("")  # blank to get the right answer
                wrong += 1
                count += 1
                
        except Exception as e:
            print(f"\nError: {e}")
            break
    
    try:
        rest = child.before.decode() if child.before else ""
        print(rest)
    except: pass
    child.close()
    print(f"\nAnswered {count} questions, {wrong} unknown")

if __name__ == "__main__":
    # Usage: python3 quiz_solver.py datafile q_idx a_idx cat1 cat2
    datafile = sys.argv[1]
    q_idx = int(sys.argv[2])
    a_idx = int(sys.argv[3])
    cat1 = sys.argv[4]
    cat2 = sys.argv[5]
    run_quiz(cat1, cat2, datafile, q_idx, a_idx)
