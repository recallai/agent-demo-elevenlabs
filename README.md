# ElevenLabs meeting agent

Send an interactive meeting agent to Zoom, Google Meet, Microsoft Teams, or Webex. It answers questions aloud and takes spoken requests to share a webpage, post in chat where supported, or leave the call.

Recall streams meeting audio directly to ElevenLabs. This Python app launches the bot and handles meeting actions through authenticated webhooks. See [Recall’s ElevenLabs integration](https://docs.recall.ai/docs/meeting-agents-elevenlabs), [Recall meeting tools](https://docs.recall.ai/docs/meeting-agents-adding-tools-to-your-meeting-agents), and [ElevenLabs webhook tools](https://elevenlabs.io/docs/eleven-agents/customization/tools/webhook-tools).

## Behavior

Address the agent as **“Assistant”** or **“elevenlabs demo”**, followed by a question or command. It joins silently. Where Recall supports meeting chat, it posts an introduction and tool feedback. Requested text and links are their own confirmation.

| Action | Tool |
| --- | --- |
| Start or replace a screen share with a public webpage | `start_screenshare(url)` |
| Post text in meeting chat | `send_chat_message(message)` |
| Post the exact last accepted page URL | `send_current_page_link()` |
| Stop the screen share while keeping voice available | `stop_screenshare()` |
| Leave the meeting | `leave_call()` |

Addressing the agent is an instruction to its model, not an enforced input filter. ElevenLabs receives the meeting's mixed audio. This native integration does not provide the app with audio controls for mute, stop-listening, or a speaking avatar.

## Requirements

- Python 3.12 and [uv](https://docs.astral.sh/uv/getting-started/installation/).
- A Recall workspace and its regional REST API key, with the native ElevenLabs agent integration available.
- An ElevenLabs account with Agents access and an API key that can create or update agents and tools.
- An HTTPS tunnel, such as cloudflared, for ElevenLabs tool callbacks.
- A meeting on one of the supported platforms.

## Quickstart

Set up and run the sample locally.

### 1. Clone the repository and install dependencies

```sh
git clone https://github.com/recallai/agent-demo-elevenlabs.git
cd agent-demo-elevenlabs
uv sync --locked
```

### 2. Configure the environment

Create the local configuration file:

```sh
cp .env.example .env
```

Fill in the root `.env`. It is ignored by Git and never sent to the browser. Existing process environment variables take precedence.

| Variable | Value |
| --- | --- |
| `RECALL_API_KEY` | REST API key for the Recall workspace. |
| `RECALL_API_BASE_URL` | Matching regional API URL, such as `https://us-east-1.recall.ai/api/v1`. |
| `ELEVENLABS_API_KEY` | ElevenLabs API key, used by the setup command. |
| `ELEVENLABS_AGENT_ID` | Leave empty initially; add the ID returned by setup. |
| `ELEVENLABS_TOOLS_ORIGIN` | The tunnel's HTTPS origin, without a path or trailing slash. |
| `ELEVENLABS_VOICE_ID` | Optional voice available to your ElevenLabs account; otherwise use its default. |
| `SESSION_TIMEOUT_SECONDS` | Session limit, from `60` to `3600` seconds; defaults to `600`. |

In the Recall region and workspace selected by your Recall API key, open **Agents → ElevenLabs**. Save an ElevenLabs key with access to the hosted agent and select the data residency region for that agent. Recall uses those settings to open the voice connection. The local app uses the ElevenLabs key only to create or update the hosted agent and its tools.

### 3. Start an HTTPS tunnel

With [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) installed:

```sh
cloudflared tunnel --url http://127.0.0.1:7862
```

Copy the tunnel's HTTPS origin into `ELEVENLABS_TOOLS_ORIGIN` in `.env`. Keep this terminal running.

Only tunnel the tool server on port **7862**. Keep the launcher on port **8002** local. Audio travels directly between Recall and ElevenLabs; it does not pass through the tunnel or this app.

### 4. Create the hosted agent and tools

Preview the configuration without making remote changes:

```sh
uv run --locked python -m app.agent --dry-run
```

Create the sample agent and its five webhook tools:

```sh
uv run --locked python -m app.agent
```

Copy the returned agent ID into `ELEVENLABS_AGENT_ID` in `.env`.

If the tunnel origin, voice, or session limit changes, refresh the same sample agent and tools:

```sh
uv run --locked python -m app.agent --update
```

Use `--update` only with the agent created for this sample: it replaces that agent's sample configuration. Restart the local app and launch a new bot after configuration changes. A temporary tunnel may receive a different origin each time it starts.

### 5. Start the app

In another terminal at the repository root:

```sh
uv run --locked python -m app.web
```

Keep this process running alongside the tunnel, then open [the launcher](http://127.0.0.1:8002).

### 6. Send the agent to a meeting

Join a Zoom, Google Meet, Microsoft Teams, or Webex meeting. Paste its direct meeting URL into the launcher and select **Send agent**. Admit **elevenlabs demo** if prompted.

### 7. Try the agent

Use the chat commands on Zoom, Google Meet, or a Teams meeting with guest chat enabled. Recall’s Webex integration supports the voice and screen sharing parts of the demo. [Recall chat support](https://docs.recall.ai/docs/sending-chat-messages)

| Try saying |
| --- |
| “Assistant, what is two plus two?” |
| “Assistant, show https://example.com.” |
| “Assistant, send the shared webpage link in chat.” |
| “Assistant, post Hello from the demo in chat.” |
| “Assistant, show https://www.recall.ai.” |
| “Assistant, send that link in chat.” |
| “Assistant, stop sharing.” |
| “Assistant, leave the meeting.” |

Confirm that a new page replaces the previous share and voice still works after sharing stops. Where chat is available, check that the exact link appears. A successful API request means Recall accepted the action; it does not prove that a webpage finished loading.

The session defaults to 10 minutes, starting when the launcher requests the bot. Expiration invalidates its tool token and requests departure. Ctrl+C also requests departure for active sessions. If departure cannot be confirmed, check the meeting or Recall dashboard before closing the tunnel. Launch another bot to repeat the demo.

## Code map

| File | Responsibility |
| --- | --- |
| `app/web.py` | Serve the local form and run the launcher and tool servers. |
| `app/meeting_url.py` | Validate meeting links. |
| `app/templates/index.html` | Meeting-URL input and launch status. |
| `app/agent.py` | Hosted agent instructions, webhook definitions, and setup/update commands. |
| `app/tool_server.py` | Authenticate callbacks, bind sessions to bots, serialize actions, and expire sessions. |
| `app/meeting_tools.py` | Five actions, chat feedback, and the last accepted page URL. |
| `app/recall_client.py` | Recall HTTP requests and clear errors. |
| `app/config.py` | Read and validate `.env`. |

The launcher creates a **four-core bot** on each supported platform using `output_media.audio.kind = "elevenlabs"` and the hosted agent ID. A per-meeting `secret__session_token` is passed through ElevenLabs [dynamic variables](https://elevenlabs.io/docs/eleven-agents/customization/personalization/dynamic-variables) into the tools' `X-Session-Token` header. The server maps that token to the bot ID returned by Recall. The model does not choose a bot ID or receive the Recall API key.

All five tools use webhook callbacks; Recall's native ElevenLabs integration does not execute client-side tools. Screen sharing uses a separate `kind: "webpage"` output, preserving the voice connection. Tool feedback failures never repeat the underlying action, and a failed share request preserves the last accepted URL.

## Boundaries and troubleshooting

- If the agent does not speak, check its ElevenLabs agent ID and the saved ElevenLabs credentials in the matching Recall workspace. Configure PCM audio with the setup command.
- If voice works but tools fail, check that the app and tunnel are running, the tunnel points to **7862**, and the hosted tool URLs match `ELEVENLABS_TOOLS_ORIGIN`. After changing the tunnel origin, run setup with `--update`.
- An invalid or expired tool session requires a newly launched bot. Restarting this app loses its in-memory sessions.
- Chat messages and shared page URLs are limited to 500 characters so the link tool can post the full URL.
- Share trusted public HTTPS webpages. The agent can display them but cannot read or interact with them; some sites may not load. Stopping sharing preserves the most recently accepted URL.
- The app does not store recordings or meeting content. Hosted agent setup disables ElevenLabs voice recording, but does not promise zero provider transcript retention. Recall recordings follow the workspace's retention settings; this app never deletes them.
- Meeting demonstrations and verification happen outside this repository. Local checks do not establish live voice, webpage rendering, or chat delivery.
