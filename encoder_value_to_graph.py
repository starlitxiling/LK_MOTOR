import re
import matplotlib.pyplot as plt

with open('log.txt', 'r', encoding='utf-8') as f:
    log_data = f.read()

encoder_values = [int(match) for match in re.findall(r"'encoder_value':\s*(\d+)", log_data)]

x = list(range(len(encoder_values)))

plt.figure(figsize=(10, 6))
plt.plot(x, encoder_values, marker='o', linestyle='-')
plt.title('Encoder Value Over Time')
plt.xlabel('Record Index')
plt.ylabel('Encoder Value')
plt.grid(True)
plt.show()