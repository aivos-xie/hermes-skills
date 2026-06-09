---
name: ai-reverse-engineering
version: 1.0.0
description: AI-powered reverse engineering tools — LLM-assisted decompilation, analysis, and binary understanding
tags: [security, reverse-engineering, ai, llm, ida, ghidra, binary-analysis]
triggers:
  - reverse engineer
  - decompile
  - binary analysis
  - RE tools
  - IDA Pro
  - Ghidra
  - disassembly
  - malware analysis
---

# AI-Powered Reverse Engineering

## Tool Overview

| Tool | Stars | Purpose | Setup |
|------|-------|---------|-------|
| ida-pro-mcp | 9,203 | IDA Pro + LLM via MCP protocol | Requires IDA Pro license |
| ghidra-mcp | 2,332 | 200+ MCP tools for Ghidra + AI | Free, open source |
| LLM4Decompile | 6,700 | LLM-based decompilation | HuggingFace models |
| reverser_ai | 1,088 | Local LLM-assisted RE | Runs entirely local |
| blutter | 2,418 | Flutter app reverse engineering | Flutter/Dart binaries |
| GDRETools/gdsdecomp | 3,710 | Godot game engine RE | .pck/.gdc/.gde files |
| Il2CppInspector | 3,008 | Unity IL2CPP RE | Unity games/apps |
| hermes-dec | 1,053 | React Native Hermes bytecode | Hermes JS engine |

---

## 1. IDA Pro + MCP (ida-pro-mcp)

**Repo:** https://github.com/mrexodia/ida-pro-mcp

Connects IDA Pro to LLMs via the Model Context Protocol, letting AI analyze binaries interactively.

### Setup

```bash
# Install the MCP server (requires IDA Pro installed)
pip install ida-pro-mcp

# Or from source
git clone https://github.com/mrexodia/ida-pro-mcp.git
cd ida-pro-mcp
pip install -e .
```

### IDA Plugin Installation

```bash
# Copy plugin to IDA plugins directory
cp ida_mcp_plugin.py "$IDA_DIR/plugins/"

# Or symlink
ln -s $(pwd)/ida_mcp_plugin.py "$IDA_DIR/plugins/"
```

### Usage

```bash
# Start MCP server (after loading a binary in IDA)
ida-pro-mcp serve

# Configure in Claude Desktop / Cursor / etc:
# Add to MCP config:
{
  "mcpServers": {
    "ida-pro": {
      "command": "ida-pro-mcp",
      "args": ["serve"]
    }
  }
}
```

### What It Exposes to LLM

- Function listing and decompilation
- Cross-references and call graphs
- String references
- Memory/segment layout
- Rename functions and variables from AI suggestions

### Pitfalls

- Requires IDA Pro license (expensive) — use Ghidra MCP as free alternative
- MCP server must be running while IDA is open
- Large binaries may exceed LLM context windows — use selective queries

---

## 2. Ghidra MCP (ghidra-mcp)

**Repo:** https://github.com/1337-ghidra-mcp/ghidra-mcp (search GitHub for latest)

200+ MCP tools exposing Ghidra's analysis capabilities to AI assistants. Free alternative to IDA MCP.

### Setup

```bash
# Install Ghidra (requires JDK 17+)
# Download from https://ghidra-sre.org/
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.3_build/ghidra_11.3_PUBLIC_20250108.zip
unzip ghidra_11.3_PUBLIC_*.zip

# Install ghidra-mcp
git clone https://github.com/leandrofriedrich/ghidra-mcp.git
cd ghidra-mcp

# Install the Ghidra extension
# Copy to Ghidra Extensions directory
cp -r ghidra_mcp_extension "$GHIDRA_DIR/Ghidra/Extensions/"

# Install Python MCP server
pip install -r requirements.txt
```

### Usage

```bash
# 1. Open binary in Ghidra, run auto-analysis
# 2. Start the MCP server
python ghidra_mcp_server.py --port 8080

# 3. Configure your AI client to connect to the MCP endpoint
```

### Key Capabilities

- Decompile functions with context
- List imports/exports
- Search for strings and patterns
- Analyze control flow graphs
- Batch analysis across functions
- Symbol renaming from AI suggestions

### Pitfalls

- Ghidra analysis on large binaries (100MB+) is slow — pre-analyze before connecting
- JDK version matters — use JDK 17, not 21+
- Some tools require Ghidra GUI to be open (headless mode is limited)

---

## 3. LLM4Decompile

**Repo:** https://github.com/AntGroup/LLM4Decompile

Fine-tuned LLMs specifically for decompilation. Reverse assembly → C code.

### Setup

```bash
# Install dependencies
pip install transformers torch accelerate

# Download models
pip install huggingface_hub
huggingface-cli download ai4compiler/LLM4Decompile-34B-V2 --local-dir ./models/llm4decompile-34b

# For smaller model (faster, less accurate)
huggingface-cli download ai4compiler/LLM4Decompile-7B-V2 --local-dir ./models/llm4decompile-7b
```

### Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_path = "./models/llm4decompile-34b"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Decompile assembly to C
assembly = """
push rbp
mov rbp, rsp
mov [rbp-0x4], edi
mov eax, [rbp-0x4]
imul eax, eax
pop rbp
ret
"""

prompt = f"Decompile the following assembly code to C:\n{assembly}\n"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Pitfalls

- 34B model needs ~70GB VRAM — use quantized versions for consumer GPUs
- Accuracy varies heavily on obfuscated or unusual compiler output
- Best results on x86_64 Linux binaries compiled with GCC/Clang
- ARM decompilation support is improving but less reliable

---

## 4. reverser_ai

**Repo:** https://github.com/cyberknight777/reverser-ai

Local LLM-assisted reverse engineering. Runs entirely offline — no data sent to cloud.

### Setup

```bash
git clone https://github.com/cyberknight777/reverser-ai.git
cd reverser-ai
pip install -r requirements.txt

# Requires Ollama or local LLM backend
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull codellama:34b
```

### Usage

```bash
# Analyze a binary
python reverser_ai.py --input malware.exe --output analysis.md

# With specific model
python reverser_ai.py --input libtarget.so --model codellama:34b --depth full
```

### Pitfalls

- Quality depends entirely on the local model — use code-specialized models
- Slower than cloud APIs for large binaries
- May miss nuanced malware behaviors that cloud models catch

---

## 5. blutter — Flutter RE

**Repo:** https://github.com/aspect-security/blutter

Reverse engineer Flutter applications by extracting Dart AOT snapshots and recovering class structures.

### Setup

```bash
git clone https://github.com/aspect-security/blutter.git
cd blutter

# Requirements: Python 3.10+, cmake, build-essential
sudo apt install cmake build-essential python3-dev

# Build
python setup.py

# Or use pre-built binaries if available
pip install blutter
```

### Usage

```bash
# Extract from Flutter app
# 1. Get libapp.so from APK
apktool d target.apk -o target_extracted
# libapp.so is in target_extracted/lib/arm64-v8a/ (or armeabi-v7a)

# 2. Run blutter
python blutter.py target_extracted/lib/arm64-v8a/libapp.so -o output/

# Output includes:
# - Recovered class names and methods
# - String literals
# - Function signatures
# - HTML report with searchable interface
```

### Pitfalls

- Flutter versions matter — blutter needs to match the Flutter SDK version used
- Obfuscated Flutter apps (flutter_obfuscate) make class recovery harder
- libapp.so location varies by build — check all lib/ subdirectories
- ARM64 is primary target; x86 support is limited

---

## 6. GDRETools/gdsdecomp — Godot RE

**Repo:** https://github.com/GDRETools/gdsdecomp

Reverse engineer Godot engine games. Recovers scripts, scenes, and resources from .pck files and compiled .gdc/.gde bytecode.

### Setup

```bash
# Download pre-built release
wget https://github.com/GDRETools/gdsdecomp/releases/latest/download/gdsdecomp-linux-x86_64.zip
unzip gdsdecomp-linux-x86_64.zip

# Or build from source
git clone https://github.com/GDRETools/gdsdecomp.git
cd gdsdecomp
scons platform=linux target=editor -j$(nproc)
```

### Usage

```bash
# GUI mode
./godsdecomp

# CLI mode — recover full project
./gdsdecomp --headless --recover game.pck

# CLI mode — recover from executable (scans for embedded .pck)
./gdsdecomp --headless --recover game.exe

# Output: full Godot project with .gd scripts, .tscn scenes, assets
```

### Pitfalls

- Godot 4.x uses different bytecode than 3.x — gdsdecomp handles both but check version
- Encrypted .pck files need the encryption key (usually hardcoded in the binary)
- Custom Godot builds may break recovery — look for version strings in the binary
- Script variable names are lost in compilation — only class/function names survive

---

## 7. Il2CppInspector — Unity IL2CPP RE

**Repo:** https://github.com/djkaty/Il2CppInspector

Recover C# code structure from Unity IL2CPP compiled binaries. Critical for Unity game RE.

### Setup

```bash
# Download release
wget https://github.com/djkaty/Il2CppInspector/releases/latest/download/Il2CppInspector-linux-x64.zip
unzip Il2CppInspector-linux-x64.zip

# Requires .NET runtime
# Install .NET 8
wget https://dot.net/v1/dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 8.0
```

### Usage

```bash
# From APK
# 1. Extract: lib/arm64-v8a/libil2cpp.so + global-metadata.dat
apktool d target.apk -o target_out

# 2. Run inspector
dotnet Il2CppInspector.dll \
  -i target_out/lib/arm64-v8a/libil2cpp.so \
  -m target_out/assets/bin/Data/Managed/Metadata/global-metadata.dat \
  -o output/

# Outputs:
# - C# stub code with class hierarchies
# - Header files for C/C++ analysis
# - IDA/Ghidra script to label all functions
# - JSON type definitions
```

### Pitfalls

- global-metadata.dat can be encrypted — check for custom loaders
- Unity version mismatch between metadata and binary causes crashes
- Some games strip debug symbols heavily — recovery is partial
- For Unity 2021+ use: https://github.com/SamboyCoding/Cpp2IL (actively maintained fork)

### Alternative: Cpp2IL

```bash
# More actively maintained for newer Unity versions
dotnet tool install -g Cpp2IL
Cpp2IL --game-path ./game_dir --output-root ./output
```

---

## 8. hermes-dec — React Native Hermes RE

**Repo:** https://github.com/nicktomlin/hermes-dec (or similar)

Decompile Hermes bytecode from React Native apps back to JavaScript.

### Setup

```bash
# Install hermes-dec
pip install hermes-dec

# Alternative: build from source
git clone https://github.com/nicktomlin/hermes-dec.git
cd hermes-dec
cargo build --release  # Rust-based
```

### Usage

```bash
# 1. Extract from React Native APK
apktool d target.apk -o target_out
# Hermes bytecode is usually in: assets/index.android.bundle

# 2. Disassemble
hermes-dec dis target_out/assets/index.android.bundle > output.dis

# 3. Decompile (partial — Hermes bytecode is lossy)
hermes-dec decompile target_out/assets/index.android.bundle > output.js

# 4. Alternative: use hermes-parser for AST
npx hermes-parser --ast target_out/assets/index.android.bundle > ast.json
```

### Pitfalls

- Hermes compilation is lossy — original JS source cannot be fully recovered
- Variable names are destroyed; only string literals and function calls survive
- Newer Hermes versions change bytecode format — tools may lag behind
- If the app uses Hermes Release mode, debugging symbols are stripped
- Look for source maps: `index.android.bundle.map` (rare in production)

---

## General RE Workflow with AI

### Recommended Pipeline

```
1. Static Analysis (Ghidra + ghidra-mcp → AI analysis)
2. Dynamic Analysis (Frida + GDB for runtime behavior)
3. LLM-Assisted Decompilation (LLM4Decompile for stubborn functions)
4. Specialized Tools (blutter/Il2CppInspector/gdsdecomp for framework targets)
5. Manual Verification (AI suggestions are hypotheses — verify them)
```

### Tips for Effective AI-Assisted RE

1. **Chunk your queries** — Don't dump entire binaries to LLMs. Feed individual functions.
2. **Provide context** — Tell the LLM what the binary does (game, malware, app) for better guesses.
3. **Cross-validate** — Use multiple tools. If Ghidra and LLM4Decompile agree, confidence is high.
4. **Rename aggressively** — Use AI-suggested names to make the IDB/Ghidra project readable.
5. **Watch for hallucinations** — LLMs may invent functionality that doesn't exist. Always verify in disassembly.

### Quick Tool Selection Guide

| Target | Primary Tool | Secondary |
|--------|-------------|-----------|
| Native ELF/PE | Ghidra + ghidra-mcp | LLM4Decompile |
| Flutter app | blutter | jadx for non-Flutter parts |
| Unity game | Il2CppInspector/Cpp2IL | Ghidra for native plugins |
| Godot game | gdsdecomp | strings/hex editor |
| React Native | hermes-dec | jadx for Java bridge |
| Android native | IDA Pro + MCP | Ghidra (free) |
| macOS/iOS | IDA Pro + MCP | Hopper Disassembler |
