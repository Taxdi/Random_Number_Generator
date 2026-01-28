from random import randint
from math import gcd
from itertools import product

p = 1000003
q =  2001911
n = p * q
seed = randint(2, n-1)

# to ensure that the seed selected randomly works for the algorithm
while gcd(seed, n) != 1:
  seed = randint(2, n-1)

bits = str(seed % 2)
for _ in range(1,10000):
  seed = (seed * seed) % n #  x_j = (x_(j-1))^2 mod n
  bit = seed % 2 # x_j, individual bit
  bits += str(bit) # concatenation of the computed seed bits

# 1. Compute the average number of 0's in a subsequence of length 1000 over all
#     such subsequences.
summation = 0
count = 0
for i in range(len(bits)-1000):
  summation += bits[i:i+1000].count("0") # count 0's in the subsequence and add them
  count += 1
average = summation / count
print("The average number of zeros per subsequence: ", average)
print()

# compute the subsequences of length 4
subseqFour = [''.join(nums)
  for nums in product('01', repeat=4)]
freq = {} # map of the subsequence frequencies in the string
for subseq in subseqFour:
  freq[subseq] = 0

# 2. Tabulate the frequency of each occurrence of the subsequence of length 4
for i in range(len(bits)-4):
    freq[bits[i:i+4]] += 1  
# Since any sequence of lenght 4 in the sequence is going to be one of the 16 
#   possible options, we use that fact to calculate the frequencies

print("Frequency of length 4 subsequences:")
print("{:<12} {:<8}".format('Subsequence', 'Count'))
for subseq in freq:
  print("{:<12} {:<8}".format(subseq, freq[subseq]))