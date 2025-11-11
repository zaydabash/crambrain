#!/bin/bash

# Script to remove emojis from node_modules files
cd /Users/zaydbashir/cram-brain

# Common emoji replacements
EMOJI_REPLACEMENTS=(
    "s/💻/computer/g"
    "s/🖌️/paintbrush/g"
    "s/🗒️/memo/g"
    "s/⭐️/star/g"
    "s/❤️/heart/g"
    "s/💿/cd/g"
    "s/📖/book/g"
    "s/📰/newspaper/g"
    "s/🏁/checkered flag/g"
    "s/👩/woman/g"
    "s/🏿/dark skin/g"
    "s/⚠️/warning/g"
    "s/🔬/microscope/g"
    "s/💥/explosion/g"
    "s/🤘/rock on/g"
    "s/🚀/rocket/g"
    "s/🚸/children crossing/g"
    "s/📣/megaphone/g"
    "s/👍/thumbs up/g"
    "s/🛠️/tools/g"
    "s/👪/family/g"
    "s/🤝/handshake/g"
    "s/🧪/test tube/g"
    "s/📝/memo/g"
    "s/📦/package/g"
    "s/💪/flexed bicep/g"
    "s/💖/sparkling heart/g"
    "s/🙏/folded hands/g"
    "s/🐛/bug/g"
    "s/📆/calendar/g"
    "s/🚧/construction/g"
    "s/🚇/metro/g"
    "s/😀/grinning face/g"
    "s/🦄/unicorn/g"
    "s/🐱/cat face/g"
    "s/🐻/bear face/g"
    "s/🌈/rainbow/g"
    "s/🐶/dog face/g"
    "s/🏎/racing car/g"
    "s/😱/face screaming in fear/g"
    "s/🔬/microscope/g"
    "s/⚠️/warning/g"
    "s/👍/thumbs up/g"
    "s/🤘/rock on/g"
)

# Process files in batches
find apps/web/node_modules -name "*.md" -o -name "*.js" -o -name "*.mjs" | while read -r file; do
    if [ -f "$file" ]; then
        # Apply all emoji replacements
        for replacement in "${EMOJI_REPLACEMENTS[@]}"; do
            sed -i '' "$replacement" "$file" 2>/dev/null || true
        done
    fi
done

echo "Emoji removal completed!"
