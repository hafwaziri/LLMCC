import sys
import torch
from transformers import RobertaTokenizer, EncoderDecoderModel

def main():

    if len(sys.argv) < 2:
        print("Usage: python inference.py <model_path> [code_file]")
        sys.exit(1)

    model_path = sys.argv[1]

    print(f"Model path: {model_path}")
    print("Loading Tokenizer and Model...")
    tokenizer = RobertaTokenizer.from_pretrained(model_path)
    model = EncoderDecoderModel.from_pretrained(model_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"Model loaded to device: {device}")


    if len(sys.argv) >= 3:
        code_file = sys.argv[2]
        print(f"Loading code from: {code_file}")
        with open(code_file, 'r') as f:
            code_snippet = f.read()
    else:
        code_snippet = """
struct s {
    int x;
    struct {
        int y;
        int z;
    } nest;
};

int
main() {
    struct s v;
    v.x = 1;
    v.nest.y = 2;
    v.nest.z = 3;
    if (v.x + v.nest.y + v.nest.z != 6)
        return 1;
    return 0;
}
"""

    input_text = f"<encoder-decoder> <c> {code_snippet}"
    inputs = tokenizer(input_text, return_tensors="pt").to(device)

    outputs = model.generate(inputs.input_ids, max_length=1024)
    generated_ir = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print("Generated Intermediate Representation (IR):")
    print(generated_ir)

if __name__ == "__main__":
    main()