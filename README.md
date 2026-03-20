# Semicon.AI

Semicon.AI: Generative AI Framework for Automated Semiconductor Chip Design 
Semicon.AI is an intelligent assistant designed to automate the Register Transfer Level (RTL) coding process. By leveraging Large Language Models (LLMs), this framework addresses the critical shortage of VLSI engineers and reduces human syntax errors in Hardware Description Languages (HDLs) like Verilog.Project Overviewtraditional chip design cycles are lengthy, expensive, and prone to errors. It serves as a "Copilot" for hardware engineers, specializing in generating syntactically accurate Verilog code from natural language prompts.

Key Results:-

110x Speedup: Generated a 4-bit Counter in 8 seconds, compared to ~15 minutes for a human engineer.

94.2% Syntax Accuracy: Performs comparably to human experts (98.6%) in producing compilable code.

Intelligent Inference: Successfully inferred complex control signals like asynchronous resets and clock-edge sensitivity in 87% of test cases.

Technical Architecture:- 

The system is built on a Transformer Decoder architecture utilizing CodeLlama-7B as the backbone. we efficiently Fine-Tuning by Low-Rank Adaptation technique (LoRA) to specialize the model for hardware design without massive computational costs, we employed Low-Rank Adaptation (LoRA):Frozen Weights: Retains general coding knowledge from the pre-trained model.

Trainable Adapters:-

Injected small rank decomposition matrices into attention layers to learn Verilog/VHDL nuances.

Dataset Details:-

The model was trained on a curated composite dataset of 18,500+ Verilog modules derived from Verilog Gen, OpenCores, and high-rated GitHub repositories.

https://github.com/klyone/opencores-ip

https://github.com/shailja-thakur/V-Gen

https://github.com/Triton-VSI/VerilogEval

The Data Distribute in certain category on the modules:-

Arithmetic Units (35%):- ALUs, Adders, Multipliers.

Sequential Logic (25%):- Counters, Shift Registers, Flip-Flops.

Control Logic (20%):- Finite State Machines (FSMs).

Interfaces (20%):- UART, SPI, I2C Controllers.

Repository StructureFinal_Model_Inference.ipynb:- The main working notebook for RTL generation.

archived_attempts and v1_failed_attempts:- Contains earlier iterations and experimental code that helped refine the final model.assets/: Diagrams and screenshots of the MVP Command Center.

How to Use Open the Final_Model_Inference.ipynb in Google Colab.

Follow the internal prompts to input a natural language description (e.g., "Create a 4-bit synchronous counter with asynchronous reset").

The system will tokenize the prompt and generate the corresponding Verilog/VHDL output.

Author :- Sparsh Pandit 



![(Semicon AI Image)](https://github.com/user-attachments/assets/d89e28c2-f691-4f24-97de-abaa2f9f3885)



![Semicon AI_elastration](https://github.com/user-attachments/assets/6dca94a7-c7cd-4409-ac4c-d2ee179a9d7e)



