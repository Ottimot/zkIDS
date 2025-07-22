from flask import Flask, request, send_file, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route("/generate_proof", methods=["POST"])
def generate_proof():
    circuitname = request.form["circuitname"]
    filename = request.form["filename"]
    command = request.form["command"]
    allowed = request.form.get("allowed", "")
    tree_path = request.form.get("tree_path", "")
    anon = request.form.get("anon", "")
    client_token = request.form.get("client_token", "")
    client_random = request.form["client_random"]
    packet_number = str(request.form["packet_number"])

    os.makedirs("files", exist_ok=True)

    # Salvataggio file ricevuti
    file_fields = {
        "provKey": f"files/provKey.bin",
        "merkle_tree": f"files/generated_merkle_tree.txt",
        "transcript": f"files/{filename}"
    }

    for field, dest_path in file_fields.items():
        if field in request.files:
            request.files[field].save(dest_path)
            print(f"Saved {field} to {dest_path}")
        else:
            print(f"Missing expected file: {field}")

    print("Generating circuit and parameters...")

    if allowed != "":
        print("Running String circuit")
        subprocess.run(f"java -cp ../xjsnark_decompiled/backend_bin_mod/:../xjsnark_decompiled/xjsnark_bin/ "
                       f"xjsnark.PolicyCheck.{circuitname} run files/{filename} {allowed} {client_random} {packet_number}", shell=True)
    elif tree_path != "":
        print("Computing proof...")
        merkle_filename = f"merkle_witness.{client_random}{packet_number}.txt"
        # Assumi che compute_proof sia disponibile nel contesto
        compute_proof(command, tree_path, anon, f"files/{merkle_filename}", "files/generated_merkle_tree.txt")

        if client_token == "":
            print("Running Merkle circuit")
            subprocess.run(f"java -cp ../xjsnark_decompiled/backend_bin_mod/:../xjsnark_decompiled/xjsnark_bin/ "
                           f"xjsnark.PolicyCheck.{circuitname} run files/{filename} files/{merkle_filename} /function {client_random} {packet_number}", shell=True)
        else:
            print("Running Merkle Token circuit")
            subprocess.run(f"java -cp ../xjsnark_decompiled/backend_bin_mod/:../xjsnark_decompiled/xjsnark_bin/ "
                           f"xjsnark.PolicyCheck.{circuitname} run files/{filename} files/{merkle_filename} {client_token} {client_random} {packet_number}", shell=True)

    print("PROOF COMPUTED!")


    subprocess.run(f"../libsnark/build/libsnark/jsnark_interface/run_zkmb files/{circuitname}.arith "
                   f"files/{circuitname}_{client_random}{packet_number}.in prove {client_random} {packet_number}", shell=True)

    # Path al file della prova generata
    proof_path = f"files/proof{client_random}{packet_number}.bin"

    if os.path.exists(proof_path):
        return send_file(proof_path, mimetype='application/octet-stream')
    else:
        return jsonify({"error": "Proof file not found"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
