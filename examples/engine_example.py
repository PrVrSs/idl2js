from pathlib import Path

from idl2js.engine import EngineConfig, FuzzEngine


EXAMPLES_DIR = Path(__file__).parent


def main():
    idl_file = str(EXAMPLES_DIR / 'canvas.webidl')

    config = EngineConfig(
        idl_type='ImageData',
        idls=(idl_file,),
        engine='node',
        timeout_ms=3000,
        seed_count=10,
        max_iterations=500,
        max_consecutive_mutations=5,
        mutation_rate=0.1,
        db_path='/tmp/idl2js_engine_db',
    )

    engine = FuzzEngine(config)

    crashes = []

    def on_crash(outcome, choices, sample):
        crashes.append(outcome)
        print(f'\n[CRASH] signal={outcome.signal}')
        for inst in sample:
            print(f'  {inst}')

    def on_interesting(outcome, choices, sample):
        print(f'  [+] {outcome.fingerprint()} ({len(choices)} choices)')

    def on_stats(stats):
        print(f'\n--- Final Stats ---')
        rate = f'{stats.exec_per_s:.1f}' if stats.exec_per_s else '0'
        print(f'Executions:    {stats.executions} ({rate} exec/s)')
        print(f'Corpus size:   {stats.corpus_size}')
        print(f'Crashes:       {stats.crashes}')
        print(f'Timeouts:      {stats.timeouts}')
        print(f'Failures:      {stats.failures}')
        print(f'Successes:     {stats.successes}')
        print(f'Chain rate:    {stats.chain_success_rate:.1%}')

    engine.on_crash(on_crash)
    engine.on_interesting(on_interesting)
    engine.on_stats(on_stats)

    print(f'Fuzzing {config.idl_type} for {config.max_iterations} iterations...')
    engine.run()

    print(f'\nTotal unique crashes: {len(crashes)}')


if __name__ == '__main__':
    main()
