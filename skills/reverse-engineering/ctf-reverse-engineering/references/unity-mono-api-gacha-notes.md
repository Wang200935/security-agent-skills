# Unity Mono gacha/API reversing notes

Use for Unity CTF games where the client contains a gacha/roll/shop API.

Observed durable pattern:

- The remote endpoint can be stored as an instance backing field initialized in a constructor, not as an obvious static constant. Inspect constructors such as `GameManager..ctor` for `ldstr http://...` followed by `stfld <GachaServerUrl>k__BackingField`.
- The parent coroutine method often only constructs `<RollCoroutine>d__N`; the actual HTTP request is in `<RollCoroutine>d__N.MoveNext`.
- Recovered UnityWebRequest shape commonly appears as:
  - `UnityWebRequest(url, "POST")`
  - `UploadHandlerRaw(Encoding.UTF8.GetBytes(json))`
  - `DownloadHandlerBuffer()`
  - `SetRequestHeader("Content-Type", "application/json")`
- JSON may be manually assembled with adjacent `ldstr` fragments and `String.Format`, e.g. fragments for `{"spend":...`, `"username":"`, and `"gold":...`.
- Treat local fallback methods as fallback only. They are useful for understanding tiers/pools, but the flag may be returned only by the recovered endpoint.

Probing discipline:

1. Start with a single short-timeout request to the exact recovered URL/path and exact recovered JSON/header.
2. Log status, headers, and the first response body before trying alternate paths.
3. Only then vary high-impact fields such as spend/rate/gold/score/kills or try path variants (`/`, `/roll`, `/gacha`, `/api/roll`).
4. Avoid one huge loop over many paths/payloads with long timeouts; it can time out before yielding any actionable result.
