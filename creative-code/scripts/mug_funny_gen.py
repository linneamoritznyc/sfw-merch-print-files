"""Generate watercolor character candidates for the SFW funny mugs on Replicate.
Character only, no text. Usage: python3 mug_funny_gen.py OUTDIR [slug ...]
Reads REPLICATE_API_TOKEN from the environment (never printed)."""
import concurrent.futures as cf
import json, os, sys, time
import requests

TOKEN = os.environ.get("REPLICATE_API_TOKEN")
if not TOKEN:
    sys.exit("REPLICATE_API_TOKEN is missing")
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "Prefer": "wait=60"}

STYLE = ("cute hand-painted watercolor illustration from a children's science picture book, soft paper texture, "
         "loose wet watercolor washes with fine ink outlines, gentle muted greens, purples and browns, "
         "single character centered, plain pure white background, generous white margin around the character, "
         "no text, no letters, no words, no logo, no frame, no border")

CHARS = {
    "compost-tea": "a grumpy sleepy nematode worm with half-closed droopy eyes and a frown, its long thin body wrapped "
                   "around a small steaming teacup full of brown tea, little wisps of steam rising",
    "bacteria": "a happy round amoeba protozoan blob with a big smile and rosy cheeks, soft translucent lavender body "
                "with a few short rounded pseudopods, several tiny rod-shaped bacteria floating around it",
    "fungi": "a smiling cute mushroom with a round brown cap and a friendly face on its stem, fine thin white fungal "
             "hyphae threads spreading out from its base like roots into a little patch of soil",
    "sommelier": "a very serious tardigrade water bear with a dignified expression, standing upright and elegantly "
                 "swirling a wine glass filled with brown compost tea, one tiny claw raised like a pinky up",
    "aerated": "a cute round soil mite with eight short legs and a happy face, blowing bubbles through a straw into "
               "a small cup of brown tea, bubbles rising out of the cup",
    "springtail": "a cute springtail insect jumping mid-air with joy, its little tail spring extended, wearing a tiny "
                  "red superhero cape flowing behind it, small motion lines",
}


def run(model, inp):
    r = requests.post(f"https://api.replicate.com/v1/models/{model}/predictions", headers=H, json={"input": inp}, timeout=120)
    if r.status_code == 429:
        time.sleep(15); return run(model, inp)
    r.raise_for_status(); p = r.json()
    while p["status"] in ("starting", "processing"):
        time.sleep(3); p = requests.get(p["urls"]["get"], headers=H, timeout=60).json()
    if p["status"] != "succeeded":
        raise RuntimeError(f"{model}: {p['status']} {p.get('error')}")
    out = p["output"]
    return out[0] if isinstance(out, list) else out


def job(outdir, slug, model, k):
    prompt = f"{CHARS[slug]}. {STYLE}"
    if model == "recraft-ai/recraft-v3":
        inp = {"prompt": prompt, "style": "digital_illustration/hand_drawn", "size": "1024x1024"}
    else:
        inp = {"prompt": prompt, "aspect_ratio": "1:1", "output_format": "png", "safety_tolerance": 2, "seed": 100 + k}
    url = run(model, inp)
    tag = "recraft" if "recraft" in model else "flux"
    path = os.path.join(outdir, f"{slug}-{tag}-{k}.png")
    open(path, "wb").write(requests.get(url, timeout=120).content)
    return path


def main():
    outdir = sys.argv[1]; slugs = sys.argv[2:] or list(CHARS)
    os.makedirs(outdir, exist_ok=True)
    jobs = [(slug, m, k) for slug in slugs for m in ("recraft-ai/recraft-v3", "black-forest-labs/flux-1.1-pro") for k in range(2)]
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {ex.submit(job, outdir, *j): j for j in jobs}
        for f in cf.as_completed(futs):
            try: print("ok", f.result())
            except Exception as e: print("fail", futs[f], str(e)[:200])


if __name__ == "__main__":
    main()
