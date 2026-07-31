import glob, re
for f in glob.glob('backend/agents/*.py'):
    content = open(f, encoding='utf-8').read()
    new_content = re.sub(r'provider=\"(groq|nvidia)\"', 'provider=\"azure\"', content)
    open(f, 'w', encoding='utf-8').write(new_content)
    print(f"Updated {f}")
