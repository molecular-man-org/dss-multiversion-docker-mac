#!/usr/bin/env bash
# api.sh — authenticated calls to a local DSS node's public API.
#
# Replaces the ad-hoc "look up the key in ~/.dataiku/config.json, hand-roll a
# client" snippet. Two properties matter more than convenience:
#
#   * it refuses any instance that is not localhost, so it cannot be pointed at
#     an internet-hosted node (those must never be changed);
#   * it always prints the HTTP status on its own last line, so a 4xx can never
#     be mistaken for an empty result. A 400 means the route exists, a 403 can
#     mean the parent project is missing, and none alone proves absence.

# api_url_is_local <url> — anchored, so userinfo tricks such as
# http://localhost:80@evil.example do not pass.
api_url_is_local() {
    [[ "$1" =~ ^http://(localhost|127\.0\.0\.1):[0-9]+$ ]]
}

# api_call <version> <METHOD> <path> [json-body]
# Body goes to stdout, then a final "HTTP <code>" line.
api_call() {
    local v="$1" method="${2:-}" path="${3:-}" body="${4:-}" url key
    case "$method" in GET|POST|PUT|PATCH|DELETE) ;;
        *) die "api: method must be GET, POST, PUT, PATCH or DELETE (got '${method}')" ;; esac
    case "$path" in /*) ;; *) die "api: path must start with / (got '${path}')" ;; esac

    url=$(instance_url "$v" | tr -d '\n')
    api_url_is_local "$url" || die "api: refusing non-local instance $url"
    key=$(apikey_from_config "$(container_name "$v")") \
        || die "api: no recorded API key for DSS $v (run: dss-lab provision $v)"

    # The key is fed through curl's config on stdin, never argv, where it would
    # be visible in `ps`.
    printf 'user = "%s:"\n' "$key" | curl -sS -m 60 -K - -X "$method" \
        -H 'Content-Type: application/json' \
        ${body:+--data "$body"} \
        -w '\nHTTP %{http_code}\n' "$url/public/api$path"
}
