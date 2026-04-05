# Task Packet - FB-096 Audio Upload, Playback, and Text-to-Speech

## Objective

Accept audio file uploads as a media type, enable playback on story cards and in the media panel, and add a browser-native text-to-speech "Listen" button on stories — so oral histories can be captured, stored, and heard alongside written narratives.

## Why / KPI

- The `audio_media_id` field on `Story` was reserved in S42 for exactly this purpose. Wiring it up now closes the loop on the stories feature.
- Audio playback of uploaded recordings is the highest-value oral history surface available today. Older family members may have voicemails, interview recordings, or home audio that they want to attach to a person's story.
- The text-to-speech "Listen" button (Web Speech API, browser-native, zero server cost) makes stories accessible to low-vision users and adds a natural way to "hear" the story without requiring an uploaded recording.
- This directly supports the G-21 AI Family Memorial long-horizon goal, which needs source audio recordings in the system.

## Scope

**In scope:**
- **Audio upload:** Accept audio MIME types (`audio/mpeg`, `audio/mp4`, `audio/ogg`, `audio/wav`, `audio/webm`) in the existing media upload flow. Audio files bypass the image-variant generation step. A waveform icon placeholder (SVG) is shown in the gallery/media panel instead of a thumbnail.
- **Audio playback:** Wherever an audio `Media` record appears (gallery, person media panel in tree sidebar, wiki page media gallery), render a standard HTML5 `<audio controls>` player pointing to the authenticated `/api/media/{id}/file` endpoint. The player is compact (height ≤ 48px) with browser default controls.
- **Story audio attachment:** On the story create/edit form, an optional "Attach audio" section lets the user link an existing audio `Media` record (by ID, or via a small picker that lists their uploaded audio files). This sets `audio_media_id` on the `Story` model. The story API `POST` and `PUT` endpoints accept `audio_media_id` as an optional field.
- **Story audio player:** If `story.audio_media_id` is set, the story card renders an `<audio controls>` player below the story body.
- **Text-to-speech "Listen" button:** Each story card gets a "Listen" button that uses `window.speechSynthesis` to read the story title + plain-text-stripped body aloud in the user's browser language. A "Stop" button appears while speech is active. No server call, no API key — purely browser-native `SpeechSynthesisUtterance`.
  - If the browser does not support `window.speechSynthesis`, the Listen button is hidden.
- i18n: add keys `stories.attach_audio` ("Attach audio"), `stories.audio_player_label` ("Voice recording"), `stories.listen` ("Listen"), `stories.stop_listening` ("Stop")

**Out of scope:**
- In-browser audio recording (microphone capture via `MediaRecorder`) — deferred
- Waveform visualisation
- Audio transcription
- Audio editing or trimming
- Server-side TTS (ElevenLabs, OpenAI, etc.) — deferred to G-21 sprint

## Task Type

- Member-facing feature — media + stories enhancement

## Dependencies

- S42 (FB-088) must be complete — `audio_media_id` column on `Story` and story API endpoints must exist
- Existing media upload flow and `/api/media/{id}/file` endpoint must exist (both do)

## Target Personas

- `contributing_member` — uploads a voicemail or recorded interview; attaches it to a story
- `mobile_first_relative` — taps "Listen" to hear a story without reading; or hears a deceased relative's voice
- `genealogy_researcher` — uploads interview recordings as primary sources

## Changed Surfaces

- Media upload modal — accept audio types, skip variant generation, show waveform placeholder
- Gallery page — audio items show `<audio>` player instead of image thumb
- Tree sidebar media panel — audio items show player
- Wiki page media gallery — audio items show player
- Story card partial — audio player if `audio_media_id` set; Listen/Stop TTS buttons
- Story add/edit form — optional audio attachment picker
- Story API (`POST`, `PUT /api/wiki/{slug}/stories`) — accept `audio_media_id` parameter
- Story list API (`GET /api/wiki/{slug}/stories`) — include `audio_media_id` in response

## Likely Files

- `app/routes/media.py` — allow audio MIME types, skip variant generation for audio
- `app/templates/gallery.html` and media panel partial — conditional audio player
- `app/templates/partials/wiki_story_card.html` — audio player and Listen/Stop buttons
- `app/templates/partials/wiki_story_form.html` — audio attachment field
- `app/routes/wiki.py` — accept `audio_media_id` in POST/PUT, include in list response
- `app/static/css/main.css` — audio player container, waveform placeholder, listen button
- `locales/en.json` + 4 others — 4 new keys

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Manual:
# Upload an MP3 file → appears in gallery with audio player (not broken image)
# Attach audio to a story → story card shows audio player
# Click Listen → browser reads the story title + body aloud
# Click Stop → speech halts

uv run pytest tests/ -k "story or media or audio" -v
uv run pytest tests/ -v
```

## Acceptance Criteria

- [ ] Audio files (mp3, m4a, wav, ogg, webm) are accepted in the upload modal without errors.
- [ ] Audio media records appear in the gallery with a waveform placeholder icon (not a broken image).
- [ ] `<audio controls>` player is rendered for audio media in the gallery, tree sidebar media panel, and wiki page media gallery.
- [ ] The audio player's `src` uses the authenticated `/api/media/{id}/file` endpoint.
- [ ] Story add/edit form has an optional "Attach audio" field for selecting an audio media ID.
- [ ] Story card renders an `<audio controls>` player below the body if `audio_media_id` is set.
- [ ] Story card has a "Listen" button that reads the story title and plain-text body via `window.speechSynthesis`.
- [ ] "Stop" button appears while speech is active; clicking it calls `speechSynthesis.cancel()`.
- [ ] "Listen" button is hidden if `window.speechSynthesis` is not supported by the browser.
- [ ] Story API `POST` and `PUT` accept optional `audio_media_id`; list response includes `audio_media_id`.
- [ ] 4 i18n keys added across all 5 locales; `test_i18n.py` passes.
- [ ] `uv run pytest tests/` passes (no regressions).

## Structural Oracle

- Gallery audio item: `audio[controls]` present, `img` absent
- Story card with audio: `audio[controls][src*="/api/media/"]` present
- Story card Listen button: `[data-story-tts-btn]` or `button` with `t('stories.listen')` text
- Story card Stop button: shown only while `speechSynthesis.speaking === true`

## Risk and Verification Notes

- **Variant generation bypass:** The current upload handler likely calls a `generate_variants()` function after saving an image. Audio files must skip this step. Guard with `if media.media_type.startswith('image/')` (or a similar MIME check) before calling variant generation.
- **Audio player and authentication:** The `<audio src="/api/media/{id}/file">` endpoint returns the file only to authenticated sessions. Browsers send cookies with audio element requests — session cookie auth works here as long as `SameSite=Lax` is set (it is). No special handling required.
- **TTS plain-text stripping:** `story.body` is HTML (Trix output). Before passing to `SpeechSynthesisUtterance`, strip HTML tags. Use a `div.innerHTML = body; div.textContent` pattern in JS — do not use regex for HTML stripping.
- **TTS language:** Set `utterance.lang` to the user's browser locale (`navigator.language`) so the OS chooses an appropriate voice.
- **Audio MIME type detection:** Validate MIME type server-side in the upload endpoint. Reject non-image, non-audio, non-video types with a clear error. Do not rely solely on file extension.
- **Waveform placeholder:** A simple inline SVG (sound wave or speaker icon) suffices. It does not need to be dynamic or reflect actual audio content.
- **Audio attachment picker on form:** Keep it simple — a plain `<input type="text" name="audio_media_id" placeholder="Audio media ID">` is acceptable for this sprint. A full media picker can come later.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Audio upload | Upload MP3 | Gallery item | Audio player shown, no broken image | 400 error or broken image |
| Playback | Click play in gallery | Audio plays | Audio plays via authenticated endpoint | 401 or silent failure |
| Story audio attachment | Attach audio to story | Story card | Audio player below story body | Player absent |
| TTS Listen | Click Listen | Speech starts | Browser reads story text | Nothing happens |
| TTS Stop | Click Stop while speaking | Speech stops | Audio halts | Speech continues |
| TTS unsupported | Browser without SpeechSynthesis | Listen button absent | Button not shown | Button shown, broken |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes
- [ ] i18n parity maintained
- [ ] Manually verified: upload audio, attach to story, playback, TTS listen/stop
