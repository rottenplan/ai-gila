import argparse
from pathlib import Path
from .engine import Engine


def main():
    parser = argparse.ArgumentParser(prog="ai-gila")
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--limit", type=int, default=10)
    g.add_argument("--seed", type=int, default=None)
    r = sub.add_parser("rank")
    r.add_argument("--limit", type=int, default=20)
    r.add_argument("--top", type=int, default=5)
    r.add_argument("--seed", type=int, default=None)
    e = sub.add_parser("evolve")
    x = sub.add_parser("export")
    x.add_argument("--seed", type=int, default=None)
    x.add_argument("--out", type=str, default="output")
    x.add_argument("--variant", type=str, default="all", help="control, urgent, minimal, or all")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    eng = Engine(root)
    if args.cmd == "generate":
        if args.seed is not None:
            eng.seed(args.seed)
        ideas = eng.generate_ideas(args.limit)
        for it in ideas:
            print(f"{it.id} | {it.title} | Trend:{it.trend_score:.2f}")
    elif args.cmd == "rank":
        if args.seed is not None:
            eng.seed(args.seed)
        ideas = eng.generate_ideas(args.limit)
        ranked = eng.rank(ideas, args.top)
        print(f"ID\tScore\tTrend\tTitle\tModel\tPrice\tAudience")
        for i, s in ranked:
            print(f"{i.id}\t{s:.4f}\t{i.trend_score:.2f}\t{i.title}\t{i.model}\tRp{int(i.price*15000):,}\t~{i.audience:,}")
    elif args.cmd == "evolve":
        eng.evolve_from_feedback()
        print("Evolusi selesai. Bobot penilaian telah diperbarui berdasarkan feedback.")
    elif args.cmd == "export":
        if args.seed is not None:
            eng.seed(args.seed)
        ideas = eng.generate_ideas(20)
        # Pick the top ranked idea
        ranked_ideas = eng.rank(ideas, 1)
        if not ranked_ideas:
            print("No ideas generated.")
            return
        idea = ranked_ideas[0][0]
        out = Path(args.out)
        
        variants = ["control", "urgent", "minimal"] if args.variant == "all" else [args.variant]
        
        print(f"Mengexport ide: {idea.title} (Score: {ranked_ideas[0][1]:.4f})")
        for v in variants:
            p = eng.export_landing_page(idea, out, v)
            print(f"- {v}: {p}")


if __name__ == "__main__":
    main()

