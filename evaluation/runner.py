import argparse
import orjson
from static_analysis.structural_analysis.llvm_ir_verification import verify_ir

def load_dataset(path, batch_size):
    batch = []
    with open(path, "rb") as f:
        for line in f:
            batch.append(orjson.loads(line))
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

def process_batch(batch):
    results = []
    for i, item in enumerate(batch):
        src = item["src"]
        ref_ir = item["ref_ir"]
        tgt_ir = item["tgt_ir"]

        # Verify IR
        ref_ir_verification, ref_ir_verification_message = verify_ir(ref_ir)
        tgt_ir_verification, tgt_ir_verification_message = verify_ir(tgt_ir)

        result = {
            'id': i,
            'ref_ir_verification': ref_ir_verification,
            'tgt_ir_verification': tgt_ir_verification,
        }

        results.append(result)

    return results

def main(args):
    for batch in load_dataset(args.dataset, args.batch_size):
        process_batch(batch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runner for Source Code Analysis")

    parser.add_argument('--dataset', type=str, required=True)
    parser.add_argument('--batch_size', type=str, default=100)

    args = parser.parse_args()

    main(args)
