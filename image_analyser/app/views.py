import os
import json
import re
import urllib.request
import urllib.error
from django.shortcuts import render, redirect
from django.conf import settings
from .models import PosterConcept

GROQ_API_KEY = getattr(settings, 'GROQ_API_KEY', '') or os.environ.get('GROQ_API_KEY', '')
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"


# ─────────────────────────────────────────────────────────────────────────────
#  SYSTEM PROMPT  —  Deep-Thinking Creative Director
#  The model first "thinks" through the topic, then produces the brief.
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an elite creative director, brand strategist, and AI image-prompt engineer with 20+ years of experience in advertising, poster design, and visual storytelling.

Your job is to deeply analyse the user's request and produce a HIGHLY SPECIFIC, CREATIVE, and ACCURATE poster concept. You do NOT give generic answers. Every single field you output must be 100% tailored to THIS specific topic, brand, audience, and context.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW YOU THINK (internal reasoning before outputting):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. DECODE THE TOPIC — What is the exact product/event/service/occasion? Who is the audience (age, gender, income, location, mindset)? What emotion should the poster trigger (excitement, trust, FOMO, warmth, aspiration)?
2. COLOUR PSYCHOLOGY — Choose colours that psychologically match this specific audience and occasion. Justify each colour choice mentally. Not generic "blue=trust" but specific: "Deep navy #1B2A4A feels aspirational for premium real estate buyers aged 35-55 in urban India".
3. VISUAL NARRATIVE — What is the ONE powerful visual story this poster tells? What scene, metaphor, or symbol captures the concept best? Think in cinematic terms.
4. TYPOGRAPHY MOOD — What font personality fits? Sharp geometric for tech, flowing serif for luxury, hand-lettered for artisan, bold slab for food?
5. COMPOSITION LOGIC — How does the viewer's eye move through this poster? What is the hero element that stops the scroll?
6. CULTURAL CONTEXT — Are there festivals, seasons, cultural symbols, or regional references that make this MORE resonant?
7. PLATFORM BEHAVIOUR — How does this specific audience consume content on each platform? What makes them stop scrolling?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Respond ONLY with valid raw JSON. No markdown, no explanation, no preamble.
- Every string must be detailed, specific, and creative — minimum 15 words for descriptive fields.
- Visual elements must describe EXACTLY what to draw/render, not vague concepts.
- AI prompts must be long, detailed, and ready to paste directly into the image tool.
- The "master_prompt" field is your CROWN JEWEL — a single 200-300 word cinematic description that a professional photographer or art director would write as a shot brief.

Output this exact JSON structure:

{
  "thinking_summary": "2-3 sentence explanation of how you interpreted this request and what creative direction you chose and why",

  "poster_title": "The actual poster headline text (compelling, not generic)",
  "poster_subtitle": "Secondary line of text that adds context or urgency",
  "tagline": "Short punchy tagline max 8 words — memorable and ownable",

  "project_description": "A rich 3-4 sentence description of what this poster is for, who it's targeting, what emotion it should evoke, and what action it should drive. Be specific about the brand/event/product context.",

  "colour_theme": {
    "primary": "#hexcode",
    "secondary": "#hexcode",
    "accent": "#hexcode",
    "background": "#hexcode",
    "text": "#hexcode",
    "highlight": "#hexcode",
    "mood": "Specific emotional mood this palette creates — be precise not generic",
    "palette_name": "Creative evocative palette name",
    "colour_rationale": "Why these exact colours work for THIS specific topic and audience — 2-3 sentences with psychological reasoning"
  },

  "visual_elements": [
    "Element 1: Extremely detailed description of exact visual — subject, pose, lighting, texture, composition role",
    "Element 2: Extremely detailed description",
    "Element 3: Extremely detailed description",
    "Element 4: Extremely detailed description",
    "Element 5: Extremely detailed description",
    "Element 6: Specific text/graphic overlay element with exact placement"
  ],

  "layout_structure": {
    "top_zone": "Exactly what appears here and why — be specific about elements and their visual treatment",
    "middle_zone": "The hero section — describe the main visual in detail",
    "bottom_zone": "CTA, contact info, brand elements — describe specifically",
    "focal_point": "The single most eye-catching element and exactly how it's designed to stop the scroll",
    "negative_space": "How empty space is deliberately used to enhance the hero element",
    "eye_flow": "How the viewer's gaze travels from entry point to CTA",
    "aspect_ratios": ["1:1 (Instagram Feed)", "4:5 (Instagram Portrait)", "9:16 (Stories/Reels)", "1.91:1 (LinkedIn/Facebook)"]
  },

  "typography": {
    "headline_font": "Exact font name — explain why it fits this brand personality",
    "subheading_font": "Exact font name and weight",
    "body_font": "Exact font name",
    "headline_size": "Size guidance relative to poster dimensions",
    "headline_treatment": "Colour, shadow, outline, gradient, or special effect on headline text",
    "special_treatment": "Any unique text effect — foil effect, emboss, neon glow, split colour, etc.",
    "google_fonts_link": "https://fonts.google.com/specimen/FontName",
    "font_pairing_reason": "Why this specific combination works for this audience and topic"
  },

  "ai_image_prompts": {
    "midjourney": "Full highly-detailed Midjourney prompt: [scene description], [style], [lighting], [colour palette], [mood], [camera angle], [quality tags] --ar 1:1 --v 6 --style raw --q 2",
    "dalle3": "Full DALL-E 3 prompt: extremely detailed description of the scene, mood, colours, composition, subject, lighting, style. Be specific. Min 100 words.",
    "stable_diffusion": "Full SD prompt with positive tags: (masterpiece:1.4), (best quality:1.4), [detailed scene], [style tags], [lighting], [colour], [composition], BREAK negative prompt: blurry, low quality, watermark, text errors",
    "leonardo": "Full Leonardo.ai prompt optimised for their engine: detailed scene, artistic style, lighting setup, colour temperature, mood atmosphere"
  },

  "master_prompt": "THE CROWN JEWEL — Write this as a professional art director's shot brief / image generation prompt. 200-300 words. Include: exact scene description, subject positioning, background environment, lighting setup (type, direction, colour, intensity), colour palette with hex codes, texture details, atmospheric effects, text overlay placement, mood and emotion, photographic or illustration style, technical quality descriptors. This should be SO detailed that any image AI or human artist can create exactly what you envision. Make it cinematic, specific, and creative.",

  "platform_trends": {
    "instagram": {
      "trending_style": "Specific current trend that fits THIS topic — not generic",
      "recommended_format": "1080x1080 or 1080x1350",
      "hook_strategy": "What specific visual hook stops the scroll for this audience",
      "caption_tip": "Specific caption writing strategy for this topic and audience",
      "hashtag_suggestion": "#relevanthashtag1 #relevanthashtag2 #relevanthashtag3 #relevanthashtag4 #relevanthashtag5",
      "story_adaptation": "How to adapt this for Stories/Reels format"
    },
    "facebook": {
      "trending_style": "Specific trend for this topic on Facebook",
      "recommended_format": "1200x628 or 1080x1080",
      "caption_tip": "Facebook-specific caption strategy for this audience",
      "ad_targeting_tip": "What Facebook audience targeting would work for this poster"
    },
    "linkedin": {
      "trending_style": "Professional angle for this topic on LinkedIn",
      "recommended_format": "1200x627",
      "caption_tip": "Professional tone caption strategy",
      "thought_leadership_angle": "How to position this poster as thought leadership content"
    },
    "whatsapp_status": {
      "trending_style": "WhatsApp-optimised design approach",
      "recommended_format": "1080x1920 (9:16 vertical)",
      "caption_tip": "Short punchy text that works with WhatsApp character limits"
    }
  },

  "design_tips": [
    "Highly specific actionable tip 1 — directly about THIS poster's design challenges",
    "Highly specific actionable tip 2 — about colour or typography application",
    "Highly specific actionable tip 3 — about making it stand out in THIS specific context"
  ],

  "similar_brand_references": [
    "Specific brand or campaign reference with explanation of why it's relevant",
    "Second specific reference with visual similarity explanation",
    "Third reference — could be a design style, photographer, or art movement"
  ],

  "print_specs": {
    "resolution": "300 DPI for print, 72-96 DPI for digital",
    "colour_mode": "CMYK for print / RGB for digital",
    "bleed": "3mm bleed on all sides for print",
    "file_format": "PDF/X-1a for print, PNG/JPG for digital",
    "size_recommendation": "Specific size recommendation for primary use case"
  }
}"""


# ─────────────────────────────────────────────────────────────────────────────
#  BUILD MASTER COMBINED PROMPT
#  Prioritises the AI's own master_prompt, enriches it with specifics
# ─────────────────────────────────────────────────────────────────────────────

def build_combined_prompt(concept: dict, user_request: str) -> str:
    """
    Build the definitive master prompt by layering:
    1. The AI's own generated master_prompt (rich, cinematic)
    2. Colour palette with exact hex codes
    3. Typography specs
    4. Layout structure
    5. Platform optimisation
    6. Technical quality suffixes
    """

    title     = concept.get("poster_title", "")
    subtitle  = concept.get("poster_subtitle", "")
    tagline   = concept.get("tagline", "")
    project   = concept.get("project_description", "")

    # ── Colour theme ──
    ct = concept.get("colour_theme", {})
    colour_block = (
        f"Exact colour palette — "
        f"background: {ct.get('background','')}, "
        f"primary: {ct.get('primary','')}, "
        f"secondary: {ct.get('secondary','')}, "
        f"accent: {ct.get('accent','')}, "
        f"text: {ct.get('text','')}, "
        f"highlight: {ct.get('highlight','')}. "
        f"Palette mood: {ct.get('mood','')}. "
        f"Named palette: '{ct.get('palette_name','')}'."
    )

    # ── Visual elements ──
    elements = concept.get("visual_elements", [])
    visual_block = "Visual elements to include: " + "; ".join(elements) + "." if elements else ""

    # ── Layout ──
    lt = concept.get("layout_structure", {})
    layout_block = (
        f"Poster layout — "
        f"TOP ZONE: {lt.get('top_zone','')}. "
        f"MIDDLE (hero): {lt.get('middle_zone','')}. "
        f"BOTTOM: {lt.get('bottom_zone','')}. "
        f"Focal point: {lt.get('focal_point','')}. "
        f"Eye flow: {lt.get('eye_flow','')}. "
        f"Negative space used as: {lt.get('negative_space','')}."
    )

    # ── Typography ──
    ty = concept.get("typography", {})
    type_block = (
        f"Typography — "
        f"Headline: '{title}' in {ty.get('headline_font','')} {ty.get('headline_size','')} "
        f"with {ty.get('headline_treatment','')}. "
        f"Subheading: '{subtitle}' in {ty.get('subheading_font','')}. "
        f"Tagline: '{tagline}'. "
        f"Special text effect: {ty.get('special_treatment','')}."
    )

    # ── Platform ──
    ig = concept.get("platform_trends", {}).get("instagram", {})
    platform_block = (
        f"Optimised for {ig.get('recommended_format','1080x1080 Instagram')} format. "
        f"Design style: {ig.get('trending_style','')}. "
        f"Scroll-stopping hook: {ig.get('hook_strategy','')}."
    )

    # ── AI's own master_prompt (the hero piece) ──
    master = concept.get("master_prompt", "")

    # ── Technical quality suffix ──
    quality_suffix = (
        "Technical specs: 4K ultra-high resolution, "
        "professional commercial advertising quality, "
        "sharp and clean composition, "
        "no watermarks, no blurriness, "
        "perfect text legibility, "
        "trending social media design aesthetic, "
        "award-winning poster design quality."
    )

    # ── Assemble: master prompt first, then all specifics ──
    if master:
        combined = (
            f"{master}\n\n"
            f"━━ POSTER TEXT ━━\n"
            f"Headline: \"{title}\" | Subtitle: \"{subtitle}\" | Tagline: \"{tagline}\"\n\n"
            f"━━ COLOUR PALETTE ━━\n{colour_block}\n\n"
            f"━━ VISUAL ELEMENTS ━━\n{visual_block}\n\n"
            f"━━ LAYOUT ━━\n{layout_block}\n\n"
            f"━━ TYPOGRAPHY ━━\n{type_block}\n\n"
            f"━━ FORMAT & PLATFORM ━━\n{platform_block}\n\n"
            f"━━ QUALITY ━━\n{quality_suffix}"
        )
    else:
        # Fallback if master_prompt wasn't generated
        combined = (
            f"Create a professional digital marketing poster for: {user_request}\n\n"
            f"Project context: {project}\n\n"
            f"━━ POSTER TEXT ━━\n"
            f"Headline: \"{title}\" | Subtitle: \"{subtitle}\" | Tagline: \"{tagline}\"\n\n"
            f"━━ COLOUR PALETTE ━━\n{colour_block}\n\n"
            f"━━ VISUAL ELEMENTS ━━\n{visual_block}\n\n"
            f"━━ LAYOUT ━━\n{layout_block}\n\n"
            f"━━ TYPOGRAPHY ━━\n{type_block}\n\n"
            f"━━ FORMAT & PLATFORM ━━\n{platform_block}\n\n"
            f"━━ QUALITY ━━\n{quality_suffix}"
        )

    return combined


# ─────────────────────────────────────────────────────────────────────────────
#  CALL GROQ API  —  uses Python's built-in urllib (zero external dependencies)
# ─────────────────────────────────────────────────────────────────────────────

def call_groq(user_request: str) -> dict:
    """
    Calls the Groq API using only Python's built-in urllib.
    No third-party packages (requests, httpx, etc.) are needed.
    This will work on any server without any pip installs.
    """

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY not set. "
            "Get your free key at https://console.groq.com "
            "then set it:  export GROQ_API_KEY=gsk_..."
        )

    # Craft a richer user message that primes the model to think deeply
    enriched_request = f"""Poster request: {user_request}

Before generating the JSON, think carefully about:
- Who exactly is the target audience for this (age, psychographic, platform behaviour)?
- What single powerful visual story tells this concept best?
- What colours will psychologically resonate with THIS audience and occasion?
- What makes this poster stop the scroll vs look generic?

Now produce the complete creative brief JSON with maximum specificity and creativity."""

    # Build the request payload as bytes (urllib requires bytes, not dict)
    payload = json.dumps({
        "model":   GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": enriched_request},
        ],
        "temperature":     0.85,
        "max_tokens":      4000,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")

    # Build the urllib request with headers
    # NOTE: User-Agent is required — Cloudflare blocks urllib's default
    # empty agent with a 403 error code 1010 (bad bot detection).
    req = urllib.request.Request(
        url=GROQ_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type":  "application/json",
            "User-Agent":    "Mozilla/5.0 (compatible; PosterMind/1.0)",
        },
    )

    try:
        # timeout=90 seconds — same as the original requests call
        with urllib.request.urlopen(req, timeout=90) as response:
            raw  = json.loads(response.read().decode("utf-8"))
            text = raw["choices"][0]["message"]["content"].strip()

    except urllib.error.HTTPError as e:
        # HTTPError carries the response body — surface it clearly
        error_body = e.read().decode("utf-8", errors="replace")[:400]
        raise Exception(f"Groq API error {e.code}: {error_body}") from e

    except urllib.error.URLError as e:
        # Network-level error (DNS failure, timeout, etc.)
        raise Exception(f"Network error reaching Groq API: {e.reason}") from e

    # Strip any accidental markdown wrappers
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)

    return json.loads(text)


# ─────────────────────────────────────────────────────────────────────────────
#  SAVE TO DATABASE
# ─────────────────────────────────────────────────────────────────────────────

def save_concept(user_request: str, concept: dict) -> PosterConcept:
    return PosterConcept.objects.create(
        user_request     = user_request,
        poster_title     = concept.get("poster_title", ""),
        colour_theme     = json.dumps(concept.get("colour_theme", {})),
        visual_elements  = json.dumps(concept.get("visual_elements", [])),
        layout_structure = json.dumps(concept.get("layout_structure", {})),
        typography       = json.dumps(concept.get("typography", {})),
        ai_prompt        = concept.get("master_prompt", "")
                          or concept.get("ai_image_prompts", {}).get("midjourney", ""),
        platform_trends  = json.dumps(concept.get("platform_trends", {})),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  DJANGO VIEWS
# ─────────────────────────────────────────────────────────────────────────────

def home(request):
    recent = PosterConcept.objects.all()[:5]
    return render(request, "home.html", {
        "recent":  recent,
        "api_set": bool(GROQ_API_KEY),
    })


def generate_poster(request):
    if request.method != "POST":
        return redirect("home")

    user_request = request.POST.get("user_request", "").strip()
    if not user_request:
        return render(request, "home.html", {
            "error":   "Please enter a poster description.",
            "api_set": bool(GROQ_API_KEY),
            "recent":  PosterConcept.objects.all()[:5],
        })

    try:
        concept         = call_groq(user_request)
        combined_prompt = build_combined_prompt(concept, user_request)
        obj             = save_concept(user_request, concept)

        context = {
            "user_request":        user_request,
            "concept":             concept,
            "obj":                 obj,
            "thinking_summary":    concept.get("thinking_summary", ""),
            "project_description": concept.get("project_description", ""),
            "poster_subtitle":     concept.get("poster_subtitle", ""),
            "colour_theme":        concept.get("colour_theme", {}),
            "visual_elements":     concept.get("visual_elements", []),
            "layout":              concept.get("layout_structure", {}),
            "typography":          concept.get("typography", {}),
            "ai_prompts":          concept.get("ai_image_prompts", {}),
            "master_prompt":       concept.get("master_prompt", ""),
            "platform_trends":     concept.get("platform_trends", {}),
            "design_tips":         concept.get("design_tips", []),
            "references":          concept.get("similar_brand_references", []),
            "print_specs":         concept.get("print_specs", {}),
            "combined_prompt":     combined_prompt,
        }
        return render(request, "results.html", context)

    except ValueError as e:
        return render(request, "home.html", {
            "error":   str(e),
            "api_set": False,
            "recent":  PosterConcept.objects.all()[:5],
        })
    except Exception as e:
        return render(request, "home.html", {
            "error":   f"Error generating concept: {str(e)}",
            "api_set": bool(GROQ_API_KEY),
            "recent":  PosterConcept.objects.all()[:5],
        })


def history(request):
    concepts = PosterConcept.objects.all()
    return render(request, "history.html", {"concepts": concepts})