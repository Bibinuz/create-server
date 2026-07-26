---
name: create-sable-fix
description: Automated diagnosis and fix for Create + Sable NullPointerException ("Cannot read field 'x' because 'mf.axis' is null") server crashes. Automatically scans MCA entity region files, safely replaces corrupted contraptions with markers, clears Sable sublevel caches, and verifies Java 21 compatibility. Activate this skill whenever the Minecraft server crashes with mf.axis null or contraption collision errors.
---

# Create + Sable Contraption Crash Resolver (`create-sable-fix`)

## Problem Overview
When running Minecraft NeoForge 1.21.1 with **Create**, **Sable**, **Create Aeronautics**, or related mods, contraptions (drills, bearings, airships, vehicles) can end up with null transformation axes (`mf.axis is null`) during collision handling in `ContraptionCollider.collideEntities` / `ContinuousOBBCollider.collideMany`.

Because Sable caches physics sublevels on disk and Minecraft loads entities when players enter render distance (~160 blocks), logging in anywhere near the contraption repeatedly triggers a server crash loop.

---

## Automated Quick Fix

When the server is offline, run the automated Python cleanup script:

```bash
python3 .gemini/skills/create-sable-fix/scripts/clean_contraptions.py
```

Or target a specific world directory:
```bash
python3 .gemini/skills/create-sable-fix/scripts/clean_contraptions.py /path/to/world
```

### What the script does:
1. **Scans Entity MCA Files**: Searches `world/entities/*.mca` for `create:stationary_contraption` and `create:oriented_contraption` NBT tags.
2. **Safely Neutralizes Corrupted Entities**: Replaces the entity type with `minecraft:marker` in-place without altering NBT alignment.
3. **Clears Sable Cache**: Deletes stale `.slvlr` and `.slvls` files in `world/sublevels/`.

---

## Manual Resolution Workflows

### Method 1: Console / In-Game Target (`/kill` by type and location)
If the server is running and players are far away from the crash zone:
```minecraft
kill @e[x=<X>,y=<Y>,z=<Z>,distance=..50,type=create:stationary_contraption]
kill @e[x=<X>,y=<Y>,z=<Z>,distance=..50,type=create:oriented_contraption]
```
Replace `<X>`, `<Y>`, `<Z>` with the contraption position.

### Method 2: Offline NBT Modification
1. Ensure server is stopped.
2. Run `python3 .gemini/skills/create-sable-fix/scripts/clean_contraptions.py`.
3. Verify Java 21 is set in `run.sh` (Minecraft 1.21.1 / NeoForge requires Java 21, e.g. `/home/bibinuz/.local/share/PrismLauncher/java/java-runtime-delta/bin/java`).
4. Restart the server using `./run.sh`.
