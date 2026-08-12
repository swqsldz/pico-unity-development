---
name: pico-unity-development
description: Develop, configure, audit, build, and troubleshoot Unity applications for PICO XR devices using the PICO Unity Integration SDK or PICO support for the Unity OpenXR Plugin. Use for PICO project setup, SDK import or migration, PXR Manager and project validation, Android manifests and permissions, XR scenes, controller or hand input, body/face/eye tracking, mixed reality and spatial sensing, rendering and performance features, compositor layers, platform services, builds, device deployment, and PICO-specific Unity errors. Consults locally refreshed Chinese and English PICO official documentation and verifies package-version-specific APIs before changing code.
---

# PICO Unity Development

Use the local official corpus as the source of truth. Inspect the project's installed packages and settings before proposing code or configuration changes.

## Start with evidence

1. Resolve the skill root as the directory containing this `SKILL.md`. Treat every `scripts/` and
   `references/` path below as relative to that skill root, not to the user's Unity project.
2. If `references/catalog.md` or `references/source-meta.json` is missing, first run the refresher
   from the skill root:

   ```powershell
   python scripts/refresh_docs.py
   ```

   If the refresh cannot access the network or otherwise fails, report the failure clearly instead of guessing documentation facts.
3. Inspect the project before editing:
   - Read `Packages/manifest.json` and `Packages/packages-lock.json`.
   - Search `Assets/`, `Packages/`, and `ProjectSettings/` for PICO packages, OpenXR features,
     `PXR_` types, Android manifests, loaders, and existing build automation.
   - Record the Unity version, render pipeline, Android target, PICO package names and versions,
     XR Plug-in Management provider, and target headset or PICO OS version when available.
4. Search the local catalog:

   ```powershell
   rg -n -i "hand tracking|gesture|PXR_Hand|手势追踪" references/catalog.md
   rg -n -i "exact API or feature" references/docs/zh references/docs/en
   ```

5. Open the most relevant local document under `references/docs/<language>/`.
   Prefer Chinese when answering in Chinese; compare the English page when wording, API spelling,
   or translation is ambiguous.
6. Verify every package-specific class, member, setting path, manifest entry, and compatibility
   claim against both the local official document and the installed package or project files. Documentation
   can be newer or older than the project.
7. State any missing version, device, entitlement, permission, or documentation field instead of
   guessing it.

## Choose the integration path

- Preserve the project's existing PICO integration unless the task explicitly requires migration.
- Distinguish the PICO Unity Integration SDK from the Unity OpenXR Plugin path. Do not mix loaders,
  feature settings, prefabs, or APIs from different paths without documentation that explicitly
  supports the combination.
- For cross-platform OpenXR work, identify which behavior is portable OpenXR and which requires a
  PICO extension.
- For upgrades, compare the installed package version with the relevant compatibility, migration,
  known-issues, and release-related documentation before editing.

## Implement safely

- Follow the project's existing assembly, namespace, prefab, scene, and build-menu conventions.
- Keep Android permissions, manifest metadata, and package names limited to documented requirements.
- Treat platform services, shared spatial data, camera data, SecureMR, and enterprise APIs as
  capability- and permission-gated. Verify device support and initialization order.
- Treat rendering settings as a coordinated system. Check render pipeline, graphics API, stereo
  mode, MSAA, color space, refresh rate, foveation, resolution scaling, compositor layers, and
  application spacewarp for documented conflicts before changing one setting.
- Preserve lifecycle symmetry: subscribe and unsubscribe events, start and stop sensing providers,
  release native resources, and handle focus or pause transitions.
- For editor changes, wait for compilation or domain reload, then check console errors before using
  newly introduced types.
- Never fabricate a `PXR_` API, OpenXR feature ID, Project Settings path, Android manifest key,
  service field, or result code.

## Validate proportionally

For implementation or configuration work:

1. Re-read the relevant official page and confirm version prerequisites.
2. Compile scripts and inspect Unity console errors.
3. Run available project validation and relevant automated tests.
4. Build a Development APK when the Android toolchain and task scope allow it.
5. On a target device, verify permissions, startup, focus transitions, tracking state, and the
   requested feature. Collect `adb logcat` evidence for runtime failures.
6. Report what was verified in Editor, what was verified on-device, and what remains unverified.

Do not describe an Editor-only check as device validation.

## Work with the local corpus

- `references/catalog.md`: searchable title, language, local-path, and source-URL index.
- `references/docs/zh/`: downloaded Chinese official pages.
- `references/docs/en/`: downloaded English official pages.
- `references/sources/<language>/llms.txt`: original PICO directory files.
- `references/source-meta.json`: fetch metadata, hashes, counts, failures, and language differences.

Search narrowly first. Do not load all pages into context. For long pages, use `rg` to locate
specific headings or symbols, then read only the relevant section.

Refresh the corpus only when the user asks for current documentation, a referenced topic is absent,
or the local metadata is stale enough to affect the task:

```powershell
python scripts/refresh_docs.py
python scripts/refresh_docs.py --check
```

Refreshing requires network access and replaces downloaded pages only after successful responses.
After refreshing, inspect `references/source-meta.json` for failed downloads or language-set
differences before relying on the corpus.

## Answer and hand off

- Cite the local official page titles used and include their original PICO URLs.
- Copy each local path and source URL from the same row of `references/catalog.md`; never infer,
  translate, or swap a Chinese and English URL by filename.
- Resolve every cited local path relative to the skill directory and verify that it exists before
  returning the answer. Do not invent line numbers; obtain them from the file when needed.
- Separate documented requirements from project-specific inference.
- Identify the tested Unity, SDK, PICO OS, and device versions when known.
- Call out compatibility gaps, device-only validation, account or entitlement requirements, and
  untested runtime behavior.
