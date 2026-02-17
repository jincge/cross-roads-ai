def main() -> None:
    """Entry point used by `python -m cross_roads_ai` (headless runner)."""
    from .main import build_simulation

    sim = build_simulation()
    print("Starting headless simulation (5 steps)")
    for i in range(5):
        sim.step()
        print(
            f"step={i+1} phase={sim.controlAlgorithm().getName()} "
            f"spawns={len(sim.recentSpawned())} "
            f"vehicle_count={sim.kpiReport().getMetrics().get('vehicle_count')}"
        )


if __name__ == "__main__":
    main()
