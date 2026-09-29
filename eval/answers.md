# End-to-end answer check (gemma3:4b, finetuned retriever, k=6)

`facts` = every expected key fact (rate, value, term) appears in the answer; `cites gold` = the answer cites a source that is a gold chunk.

| Slice | n | gold retrieved | key facts in answer | cites a gold source |
|---|---|---|---|---|
| all | 47 | 96% | 79% | 77% |
| bsr | 16 | 100% | 88% | 88% |
| is456 | 16 | 100% | 69% | 62% |
| pmgsy | 15 | 87% | 80% | 80% |

Mean latency 12.8s per question (retrieval + generation).

### is-01 — ✓ facts · ✓ cites gold
**Q:** What minimum nominal cover should be provided to reinforcement for 'severe' exposure conditions?  
**Expected:** 45 mm (Table 16); may be reduced by 5 mm for M35 and above  
**Sources:** [1] IS 456:2000 Table 16; [2] IS 456:2000 Clause 26.4.2 – 26.5.1.1; [3] IS 456:2000 Foreword; [4] IS 456:2000 Clause 8.2.2.3 – 8.2.4; [5] IS 456:2000 Clause 8.2 – 8.2.2.1; [6] IS 456:2000 Table 3 – 8.2.2.2

According to source [1], for ‘severe’ exposure conditions, the nominal concrete cover should not be less than 45 mm. [1]

### is-02 — ✗ facts · ✓ cites gold
**Q:** For reinforced concrete in a severe exposure environment, what is the minimum cement content, maximum water-cement ratio and minimum grade?  
**Expected:** 320 kg/m3, 0.45, M30 (Table 5)  
**Sources:** [1] IS 456:2000 Table 5; [2] IS 456:2000 Clause 8.2.4.1 – 8.2.4.2; [3] IS 456:2000 Table 3 – 8.2.2.2; [4] IS 456:2000 Clause 8.2.2.3 – 8.2.4; [5] IS 456:2000 Foreword; [6] IS 456:2000 Clause 8.2 – 8.2.2.1

According to [1], for reinforced concrete in a severe exposure environment:

*   Minimum cement content: 250 kg/m*
*   Maximum water-cement ratio: 0.50
*   Minimum grade of concrete: M25

### is-03 — ✓ facts · ✓ cites gold
**Q:** What are the limits on longitudinal reinforcement percentage in a column?  
**Expected:** Not less than 0.8% nor more than 6% of gross area (26.5.3.1)  
**Sources:** [1] IS 456:2000 Clause 26.5.3.1; [2] IS 456:2000 Clause B-3.3 – B-3.4; [3] IS 456:2000 Clause 26.5.3.2; [4] IS 456:2000 Clause 41.3.1 – 41.4.2; [5] IS 456:2000 Clause 34.4.1 – 34.5.1; [6] IS 456:2000 Clause 26.5.3.3

The longitudinal reinforcement percentage in a column shall not be less than 0.8 percent nor more than 6 percent of the gross cross-sectional area [1].

### is-04 — ✓ facts · ✓ cites gold
**Q:** basic span to effective depth ratio simply supported beam deflection control  
**Expected:** 20 for simply supported (7 cantilever, 26 continuous), spans up to 10 m  
**Sources:** [1] IS 456:2000 Clause 28.2 – 28.2.1; [2] IS 456:2000 Clause 23.2; [3] IS 456:2000 Clause 24 – 24.2; [4] IS 456:2000 Clause 22 – 22.2; [5] IS 456:2000 Clause 22.4.1 – 22.4.2; [6] IS 456:2000 Clause 29 – 29.1

For a simply supported beam, the basic value of span to effective depth ratio is 20 [2].

*   For spans up to 10 meters, the ratio is 20 [2].
*   For spans above 10 meters, the value may be multiplied by 10/span, except for cantilever beams [2].

### is-05 — ✗ facts · ✓ cites gold
**Q:** How many cube samples do I need to take if 40 m3 of concrete of one grade is placed?  
**Expected:** 4 samples (31-50 m3)  
**Sources:** [1] RHB BSR 2024 Item B-4.6.4; [2] IS 456:2000 Clause 15.2.2 – 15.4; [3] RHB BSR 2024 Item B-3.1.3; [4] RHB BSR 2024 Notes, page B-160; [5] IS 456:2000 Clause 16.3 – 16.6; [6] RHB BSR 2024 Item G-769

According to [2], if the quantity of concrete is between 1-5 m*, then 1 sample is required. If the quantity is between 6-15 m*, then 2 samples are required. Therefore, for 40 m3 of concrete, you need to take 2 samples.

### is-06 — ✓ facts · ✓ cites gold
**Q:** How can the flexural strength of concrete be estimated from the characteristic cube strength?  
**Expected:** fcr = 0.7 sqrt(fck) N/mm2  
**Sources:** [1] IS 456:2000 Clause 16 – 16.2; [2] IS 456:2000 Clause 6.2.2 – 6.2.4; [3] IS 456:2000 Clause 17.4.1 – 17.6.1; [4] IS 456:2000 Clause 4; [5] IS 456:2000 Table 2 – 6.2.1.2; [6] IS 456:2000 Clause 38.1

According to [2], the flexural strength, f, can be estimated using the following formula:

f, = 0.7[f, N/mm?]

where f, is the characteristic cube compressive strength of concrete in N/mm?. 

This relates to Item Code: Concrete Strength Estimation. Close variants include M10, M20, M25, M30, M35, M40, M45, M50, M60, M65, M78, M80, and M170.

### is-07 — ✓ facts · ✗ cites gold
**Q:** What value of modulus of elasticity should be assumed for steel reinforcement?  
**Expected:** 200 kN/mm2 (5.6.3)  
**Sources:** [1] IS 456:2000 Clause 5.6.2 – 5.7; [2] IS 456:2000 Clause 36.4.2.2; [3] IS 456:2000 Clause 38.1; [4] IS 456:2000 Clause 6.2.2 – 6.2.4; [5] IS 456:2000 Annex F; [6] IS 456:2000 Annex B – B-1.3

According to [3], the modulus of elasticity of steel shall be taken as 200 kN/mn®.

### is-08 — ✓ facts · ✗ cites gold
**Q:** What is the maximum pitch allowed for helical reinforcement in a column?  
**Expected:** Not more than 75 mm nor more than one-sixth of core diameter  
**Sources:** [1] IS 456:2000 Clause 26.5.3.2; [2] IS 456:2000 Clause 26.5.3.1; [3] IS 456:2000 Clause 26.5.3.2; [4] IS 456:2000 Clause 39.7 – 39.7.1; [5] IS 456:2000 Clause B-3.1 – B-3.2; [6] IS 456:2000 Clause B-3.3 – B-3.4

According to [2], the pitch of helical turns shall be not more than 75 mm, nor more than one-sixth of the core diameter of the column, nor less than 25 mm, nor less than three times the diameter of the steel bar forming the helix.

### is-09 — ✓ facts · ✓ cites gold
**Q:** Partial safety factor on loads for dead load plus imposed load at the limit state of collapse  
**Expected:** 1.5 (Table 18)  
**Sources:** [1] IS 456:2000 Clause 36.3.1 – 36.4.2.1; [2] IS 456:2000 Table 18; [3] IS 456:2000 Clause 35.1.2 – 35.3.1; [4] IS 456:2000 Clause 20 – 20.3; [5] IS 456:2000 Clause 19.5.1 – 19.9; [6] IS 456:2000 Clause 39.7.1.1

The partial safety factor on loads for dead load plus imposed load at the limit state of collapse is 1.5 [2].

### is-10 — ✗ facts · ✗ cites gold
**Q:** What is the maximum unsupported length of a column in terms of its least lateral dimension?  
**Expected:** 60 times the least lateral dimension (25.3.1)  
**Sources:** [1] IS 456:2000 Clause 25.2 – 25.4; [2] IS 456:2000 Clause 25.1.3; [3] IS 456:2000 Annex E – E-1; [4] IS 456:2000 Clause B-3.3 – B-3.4; [5] IS 456:2000 Clause E-2 – E-3; [6] IS 456:2000 Clause 39.5

According to [25.3.2], the unsupported length, /, shall not exceed 1006% D where b = width of that cross-section, and D = depth of the cross-section measured in the plane under consideration. 

Specifically, the source states: “25.3.2 If, in any given plane, one end of a column is unrestrained, its unsupported length, /, shall not exceed 1006% D where b = width of that cross-section, and D = depth of the cross-section measured in the plane under consideration.”

### is-11 — ✓ facts · ✓ cites gold
**Q:** Is it acceptable to use sea water for mixing or curing reinforced concrete?  
**Expected:** Not recommended; only plain concrete with no embedded steel under unavoidable circumstances (5.4.3)  
**Sources:** [1] IS 456:2000 Clause 5.4.3 – 5.5.1; [2] IS 456:2000 Clause 8.2.7 – 8.2.8.1; [3] IS 456:2000 Table 10 – 10.3; [4] IS 456:2000 Clause 5.3.4 – 5.4.1; [5] IS 456:2000 Clause 8.2.8.2 – 8.2.8.4; [6] IS 456:2000 Table 3 – 8.2.2.2

No, it is not acceptable to use sea water for mixing or curing reinforced concrete [1][2]. 

Here’s a breakdown of the relevant points:

*   Sea water is generally not recommended for mixing or curing plain concrete due to the presence of harmful salts [1].
*   For reinforced concrete, M20 grade concrete is required in sea water conditions [2].
*   Special attention should be given to the mix design to ensure densest possible concrete [2].

### is-12 — ✗ facts · ✗ cites gold
**Q:** What is the minimum area of tension steel required in a beam?  
**Expected:** As/(bd) = 0.85/fy (26.5.1.1)  
**Sources:** [1] IS 456:2000 Clause 25.1.2; [2] IS 456:2000 Clause 29.3 – 29.3.1; [3] IS 456:2000 Clause 23.2; [4] IS 456:2000 Clause 29.3.2 – 29.3.3; [5] IS 456:2000 Clause 26.4.2 – 26.5.1.1; [6] IS 456:2000 Table 22

According to [3], the minimum area of tension steel required in a beam is equal to b, d.

### is-13 — ✓ facts · ✓ cites gold
**Q:** When is concrete considered to comply with the specified compressive strength during acceptance?  
**Expected:** Mean of 4 consecutive results and each individual result meet Table 11 limits (16.1)  
**Sources:** [1] IS 456:2000 Clause 16 – 16.2; [2] IS 456:2000 Clause 15 – 15.2.1; [3] IS 456:2000 Clause 16.3 – 16.6; [4] IS 456:2000 Table 2 – 6.2.1.2; [5] IS 456:2000 Clause 8 – 8.1.1; [6] IS 456:2000 Clause 38.1

The concrete is considered to comply with the specified compressive strength during acceptance if both of the following conditions are met [1]:

*   The mean strength determined from any group of four consecutive test results complies with the appropriate limits in col 2 of Table 11 [1].
*   Any individual test result complies with the appropriate limits in col 3 of Table 11 [1].

### is-14 — ✓ facts · ✗ cites gold
**Q:** Which exposure condition applies to concrete that is completely immersed in sea water?  
**Expected:** Severe (Table 3)  
**Sources:** [1] IS 456:2000 Table 3 – 8.2.2.2; [2] IS 456:2000 Clause 5.4.3 – 5.5.1; [3] IS 456:2000 Clause 8.2.6.1 – 8.2.6.2; [4] IS 456:2000 Clause 8.2.7 – 8.2.8.1; [5] IS 456:2000 Clause 8.2 – 8.2.2.1; [6] IS 456:2000 Clause 8 – 8.1.1

According to source [8], concrete completely immersed in sea water falls under the “Very severe” environment exposure condition. [8]

### is-15 — ✓ facts · ✗ cites gold
**Q:** Up to which grade is nominal mix concrete permitted?  
**Expected:** M20 or lower (9.3)  
**Sources:** [1] IS 456:2000 Clause 9 – 9.1.1; [2] IS 456:2000 Clause 9.1.2 – 9.2.1; [3] IS 456:2000 Clause 9.3 – Table 9; [4] RHB BSR 2024 Item B-3.1.3; [5] RHB BSR 2024 Item B-3.1.2; [6] IS 456:2000 Clause 9.2.2 – 9.2.4

Nominal mix concrete may be used for concrete of M 20 or lower [1].

### is-16 — ✗ facts · ✓ cites gold
**Q:** What spacing between lateral restraints is permitted to keep a beam laterally stable?  
**Expected:** Clear distance not more than 60b or 250b^2/d, whichever is less (23.3)  
**Sources:** [1] IS 456:2000 Clause 23.3; [2] IS 456:2000 Clause 25.1.3; [3] IS 456:2000 Clause 26.5.1.2 – 26.5.1.5; [4] IS 456:2000 Clause 23 – 23.1.1; [5] IS 456:2000 Clause 22.4.1 – 22.4.2; [6] IS 456:2000 Clause 32.2.1

The clear distance between lateral restraints for a simply supported or continuous beam shall not exceed 60b or = whichever is less, where d is the effective depth of the beam and b the breadth of the compression face midway between the lateral restraints [1]. For a cantilever, the clear distance from the free end of the cantilever to the lateral restraint shall not exceed 25b or whichever is less [1].

### bsr-01 — ✓ facts · ✓ cites gold
**Q:** Rate for excavating a trench for pipes up to 80 mm diameter in hard rock where blasting is needed  
**Expected:** Rs 265 per metre  
**Sources:** [1] RHB BSR 2024 Item B-1.8.2.1; [2] RHB BSR 2024 Item B-1.8.2.2; [3] RHB BSR 2024 Item B-1.8.3.1; [4] RHB BSR 2024 Item B-1.8.3.2; [5] RHB BSR 2024 Item B-1.8.2.3; [6] RHB BSR 2024 Item B-1.8.3.3

The rate for excavating a trench for pipes up to 80mm diameter in hard rock where blasting is needed is Rs. 265.00 per Mtr. [1] 

*   This rate corresponds to Item B-1.8.2.1.
*   Close variants include:
    *   Pipes exceeding 80mm dia but not exceeding 300mm dia – Rs. 655.00 per Mtr. [2]
    *   Pipes not exceeding 80mm dia – Rs. 349.00 per Mtr. [3]

### bsr-02 — ✓ facts · ✓ cites gold
**Q:** What is the basic rate of a 400 mm ductile iron class K-9 pipe to IS 8329?  
**Expected:** Rs 5260 per metre  
**Sources:** [1] RHB BSR 2024 Item G-7657; [2] RHB BSR 2024 Item G-7658; [3] RHB BSR 2024 Item G-7664; [4] RHB BSR 2024 Item G-7663; [5] RHB BSR 2024 Item G-7692; [6] RHB BSR 2024 Item G-7660

The basic rate for a 400mm ductile iron class K-9 pipe conforming to I.S. 8329 is Rs. 5260.00 per Mtr. [1]

*   This corresponds to Material/Labour code G-7657.
*   A 450mm diameter pipe (G-7658) has a rate of Rs. 5850.00 per Mtr. [2]
*   A 600mm diameter pipe (G-7660) has a rate of Rs. 8770.00 per Mtr. [6]

### bsr-03 — ✓ facts · ✓ cites gold
**Q:** How much do chromium plated brass butt hinges of 125x70x4 mm cost?  
**Expected:** Rs 1150 per 10 Nos  
**Sources:** [1] RHB BSR 2024 Item G-525; [2] RHB BSR 2024 Item G-378; [3] RHB BSR 2024 Item G-526; [4] RHB BSR 2024 Item G-527; [5] RHB BSR 2024 Item G-382; [6] RHB BSR 2024 Item G-524

The cost of chromium plated brass butt hinges of 125x70x4 mm is Rs. 1150.00 per 10 Nos [1].

*   There are two items with this dimension:
    *   G-525: Chromium plated Brass butt hinges (light/ordinary) type 125x70x4 mm - Rs. 1150.00 [1]
    *   G-378: Brass butt hinges (light/ordinary type): 125x70x4 mm - Rs. 650.00 [2]

### bsr-04 — ✓ facts · ✓ cites gold
**Q:** What is the rate for providing and fixing a lock on a drawer?  
**Expected:** Rs 422 each  
**Sources:** [1] RHB BSR 2024 Item B-8.49; [2] RHB BSR 2024 Item B-8.48.1; [3] RHB BSR 2024 Item B-8.39; [4] RHB BSR 2024 Item B-8.48.2; [5] RHB BSR 2024 Item E-27.43.7; [6] RHB BSR 2024 Item G-8718

The rate for providing and fixing a drawer lock is Rs. 422.00 [1].

*   This is for a drawer lock of an approved make, complete with screws, as per the engineer in charge’s approval.
*   There are several related items:
    *   B-8.48.1: Rs. 150.00 for a 100mm drawer handle [2]
    *   B-8.48.2: Rs. 184.00 for a 150mm drawer handle [4]
    *   B-8.39: Rs. 141.00 for an Almirah lock (50-70mm size) without handles [3]
    *   G-8718: Rs. 240.00 for an Almirah lock of approved make (Godrej or equivalent) [6]

### bsr-05 — ✓ facts · ✓ cites gold
**Q:** cost of renewing old putty on glass panes per running metre  
**Expected:** Rs 17 per Rm  
**Sources:** [1] RHB BSR 2024 Item B-13.8; [2] RHB BSR 2024 Item B-13.9; [3] RHB BSR 2024 Item B-13.4.2; [4] RHB BSR 2024 Item B-13.4.1; [5] RHB BSR 2024 Item B-13.6.1; [6] RHB BSR 2024 Item B-13.6.2

The cost of renewing old putty on glass panes is Rs. 17.00 per metre [1].

*   This corresponds to Item B-13.8.
*   The unit of measurement is Rm (Ringgit Malaysia) [1].

### bsr-06 — ✗ facts · ✗ cites gold
**Q:** What is the rate of an 18.5 kW centrifugal monoblock pump set including installation and commissioning?  
**Expected:** Rs 1,56,300 each  
**Sources:** [1] RHB BSR 2024 Item S-5.53.1.8; [2] RHB BSR 2024 Item S-5.53.2.6; [3] RHB BSR 2024 Item S-5.56.2; [4] RHB BSR 2024 Item S-5.53.2.2; [5] RHB BSR 2024 Item S-5.53.1.3; [6] RHB BSR 2024 Item S-5.53.2.5

The rate for an 18.5 kW centrifugal monoblock pump set, including installation and commissioning, is Rs. 340774.00 [3].

### bsr-07 — ✓ facts · ✓ cites gold
**Q:** Rate for a manually operated 250 mm knife gate valve on a sewage line  
**Expected:** Rs 41,000 each  
**Sources:** [1] RHB BSR 2024 Item S-6.101.6; [2] RHB BSR 2024 Item S-6.101.5; [3] RHB BSR 2024 Item S-6.101.3; [4] RHB BSR 2024 Item S-6.101.10; [5] RHB BSR 2024 Item S-6.101.4; [6] RHB BSR 2024 Item S-6.101.7

The rate for a manually operated 250 mm knife gate valve is Rs. 41000.00 [1]. 

*   This corresponds to Item S-6.101.6.
*   Variants with different diameters (200 mm, 125 mm, 450 mm, 300 mm, 150 mm) are available at different rates [2][3][4][5][6].

### bsr-08 — ✓ facts · ✓ cites gold
**Q:** What does it cost per metre to lay a 400 mm HDPE PE-100 PN6 sewer pipe?  
**Expected:** Rs 6950 per metre  
**Sources:** [1] RHB BSR 2024 Item S-6.28.6; [2] RHB BSR 2024 Item S-6.28.7; [3] RHB BSR 2024 Item S-6.85.5; [4] RHB BSR 2024 Item S-6.28.3; [5] RHB BSR 2024 Item S-5.5.2.2; [6] RHB BSR 2024 Item S-6.28.8

It costs Rs. 6950.00 per metre to lay a 400 mm HDPE PE-100 PN6 sewer pipe [1]. 

*   There is also a rate of Rs. 26300.00 per metre for replacing pipelines using pneumatic/static pipe bursting, which includes similar pipe specifications [3].
*   A 250 mm HDPE PE-100 PN6 sewer pipe costs Rs. 2665.00 per metre [4].

### bsr-09 — ✓ facts · ✓ cites gold
**Q:** Hire charges per day for a 7-lamp cut glass chandelier with operator  
**Expected:** Rs 237 each per day; subsequent days 50%  
**Sources:** [1] RHB BSR 2024 Item E-25.46; [2] RHB BSR 2024 Item E-25.44; [3] RHB BSR 2024 Item E-25.45; [4] RHB BSR 2024 Item G-7; [5] RHB BSR 2024 Item E-25.36; [6] RHB BSR 2024 Item E-25.50

The hire charge per day for a 7-lamp cut glass chandelier with an operator is Rs. 237.00 [1]. 

*   This is Item E-25.46.
*   The rates for subsequent days are 50% of the original rate [1].
*   Close variants include a 20-lamp chandelier (Rs. 678.00 [2]) and a 15-lamp chandelier (Rs. 509.00 [3]).

### bsr-10 — ✓ facts · ✓ cites gold
**Q:** Rate of 38 mm x 25 mm UPVC trunking with accessories  
**Expected:** Rs 98 per running metre  
**Sources:** [1] RHB BSR 2024 Item E-3.4.6; [2] RHB BSR 2024 Item E-3.4.7; [3] RHB BSR 2024 Item E-3.4.5; [4] RHB BSR 2024 Item E-3.4.2; [5] RHB BSR 2024 Item E-3.4.4; [6] RHB BSR 2024 Item E-3.4.3

The rate for 38 mm x 25 mm UPVC trunking with accessories is Rs. 98.00 per meter [1].

*   This corresponds to Item E-3.4.6.
*   Close variants include 38 mm x 38 mm (Rs. 126.00 per meter [2]) and 38 mm x 16 mm (Rs. 88.00 per meter [3]).

### bsr-11 — ✓ facts · ✓ cites gold
**Q:** Extra rate for sewer excavation with dewatering when the water table is met between 3 and 4.5 m depth  
**Expected:** Rs 239 per cum  
**Sources:** [1] RHB BSR 2024 Item S-6.2.1.3; [2] RHB BSR 2024 Item S-6.2.1.4; [3] RHB BSR 2024 Item S-6.2.1.2; [4] RHB BSR 2024 Item S-6.2.1.1; [5] RHB BSR 2024 Item S-6.1.4.3; [6] RHB BSR 2024 Item S-6.1.2.3

The rate for sewer excavation with dewatering when the water table is between 3.0 to 4.5 m depth is Rs. 239.00 per Cum [1]. 

*   This rate applies to Item S-6.2.1.3.
*   Close variants include:
    *   Rs. 359.00 per Cum for a water table depth between 4.5 to 6.0 m [2].

### bsr-12 — ✓ facts · ✓ cites gold
**Q:** What is the rate for precast RCC lintels up to 1.5 m clear span in M20?  
**Expected:** Rs 9163 per cum  
**Sources:** [1] RHB BSR 2024 Item B-4.18.2; [2] RHB BSR 2024 Item B-4.18.4; [3] RHB BSR 2024 Notes, page S-128; [4] RHB BSR 2024 Item S-6.61; [5] RHB BSR 2024 Item B-4.18.1; [6] RHB BSR 2024 Item B-4.17

The rate for precast RCC lintels up to 1.5 m clear span in M20 is Rs. 9163.00 per Cum [1].

### bsr-13 — ✗ facts · ✗ cites gold
**Q:** How much extra is allowed for pipe trench excavation deeper than 1.5 m but not exceeding 3 m?  
**Expected:** 1.41% extra  
**Sources:** [1] RHB BSR 2024 Item B-1.9; [2] RHB BSR 2024 Item B-1.10; [3] RHB BSR 2024 Item B-1.6; [4] RHB BSR 2024 Item B-1.7; [5] RHB BSR 2024 Item B-1.5.3; [6] RHB BSR 2024 Item B-1.15.2

According to Item B-1.9, an extra of 104% is allowed for pipe trench excavation deeper than 1.5 m but not exceeding 3 m [1]. 

*   This extra applies over the corresponding basic item for depths up to 1.5 m.
*   The item code is B-1.9 and the description is “Add extra for excavating trenches for pipes, cables, etc. in ordinary/hard rock exceeding 1.5 m in depth but not exceeding 3 m.”

### bsr-14 — ✓ facts · ✓ cites gold
**Q:** Road work rate for excavation for structures in marshy soil  
**Expected:** Rs 380 per cum  
**Sources:** [1] RHB BSR 2024 Item R-1.12; [2] RHB BSR 2024 Item R-7.1; [3] RHB BSR 2024 Item R-1.11; [4] RHB BSR 2024 Notes, page S-132; [5] RHB BSR 2024 Notes, page S-131; [6] RHB BSR 2024 Notes, page S-130

The rate for excavation for structures in marshy soil is Rs. 380.00 per Cum [2]. 

*   This rate is specifically for marshy soil excavation [2].
*   The item code is R-7.1 and the description is “Marshy soil” [2].

### bsr-15 — ✓ facts · ✓ cites gold
**Q:** rate for providing ball bearings for a rolling shutter  
**Expected:** Rs 537 each  
**Sources:** [1] RHB BSR 2024 Item B-9.10; [2] RHB BSR 2024 Item G-976; [3] RHB BSR 2024 Item G-973; [4] RHB BSR 2024 Item B-13.26; [5] RHB BSR 2024 Item B-9.12; [6] RHB BSR 2024 Item B-13.27

The rate for providing and fixing ball bearings for rolling shutters is Rs. 537.00 per unit [1].

*   This rate is associated with Item B-9.10.
*   There is a similar rate of Rs. 450.00 per unit for ball bearings for rolling shutters, but this is associated with a different item code (G-976) [2].

### bsr-16 — ✓ facts · ✓ cites gold
**Q:** What does item B-1.5.2 cover and what is its rate?  
**Expected:** Trench excavation for pipes/cables 80-300 mm dia in all kinds of soil, Rs 161 per metre  
**Sources:** [1] RHB BSR 2024 Item B-1.5.2; [2] RHB BSR 2024 Page 8; [3] RHB BSR 2024 Notes, page S-93; [4] RHB BSR 2024 Notes, page S-14; [5] RHB BSR 2024 Item G-7326; [6] RHB BSR 2024 Notes, page S-13

Item B-1.5.2 covers pipes cables, etc. exceeding 80mm dia but not exceeding 300mm dia [1]. The rate for this item is Rs. 161.00 per Mtr. [1].

### pm-01 — ✗ facts · ✓ cites gold
**Q:** When was PMGSY launched and how is it funded?  
**Expected:** 25 Dec 2000; 100% centrally sponsored; 50% of the cess on high speed diesel earmarked  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 1.2; [2] PMGSY Guidelines (Hindi) पैरा 13; [3] PMGSY Guidelines (Hindi) पैरा 9; [4] PMGSY Guidelines (Hindi) पृष्ठ 1; [5] PMGSY Guidelines (Hindi) पैरा 18–18.2; [6] PMGSY Guidelines (Hindi) पैरा 17–17.1

PMGSY was launched on December 25, 2000 [1]. It is funded by the central government at 50% on High Speed Diesel (HSD) rates [1].

### pm-02 — ✗ facts · ✗ cites gold
**Q:** On what basis should a state distribute its PMGSY allocation among districts?  
**Expected:** 80% on road length needed to connect unconnected habitations, 20% on length to be upgraded  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 3.9; [2] PMGSY Guidelines (Hindi) पैरा 6.12; [3] PMGSY Guidelines (Hindi) पैरा 2.2; [4] PMGSY Guidelines (Hindi) पैरा 17–17.1; [5] PMGSY Guidelines (Hindi) पैरा 2–2.1; [6] PMGSY Guidelines (Hindi) पैरा 7–7.1

According to [3], “यह नोट किया जाए कि सुधार-कार्य कार्यक्रम का केन्द्र बिन्दु नहीं है और ऐसी स्थिति में जहां अभी भी सड़कों से न जुड़ी पात्र बसावटें मौजूद हैं यह उन राज्यों के राज्य आवंटन के 20 % से अधिक नहीं हो सकता ।” 

This indicates that a state’s PMGSY allocation should not exceed 20% of its total allocation to districts where eligible settlements are still not connected to roads.

### pm-03 — ✗ facts · ✓ cites gold
**Q:** What special allocation is made for districts bordering Pakistan and China?  
**Expected:** Up to 5% of the annual allocation from the rural roads share of the diesel cess  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 5.3; [2] PMGSY Guidelines (Hindi) पैरा 6.6.1; [3] RHB BSR 2024 Notes, page G-2; [4] PMGSY Guidelines (Hindi) पैरा 13; [5] RHB BSR 2024 Page M-105; [6] PMGSY Guidelines (Hindi) पैरा 9

According to [1], special allocation is made for districts bordering Pakistan and China, “निम्न के लिए : () पाकिस्तान और चीन की सीमा से जुड़े राज्यों के जिले (गृह मंत्रालय के समन्वय से);”.

### pm-04 — ✓ facts · ✗ cites gold
**Q:** Are urban roads eligible under the scheme?  
**Expected:** No, only rural roads classified as Other District Roads and Village Roads  
**Sources:** [1] RHB BSR 2024 Page M-105; [2] PMGSY Guidelines (Hindi) पैरा 8.5; [3] PMGSY Guidelines (Hindi) पैरा 6.3; [4] PMGSY Guidelines (Hindi) पैरा 1–1.1; [5] PMGSY Guidelines (Hindi) पैरा 2.2; [6] PMGSY Guidelines (Hindi) पैरा 12.3

No. [3] states that “पीसीआई वाली पक्की अच्छी बारहमासी सड़कों और +40 वर्ष से कम पुरानी पक्की अच्छी बारहमासी सड़कों (यदि पी सी ई 2 से कम हो तो भी ) की फिलहाल मरम्मत नहीं की जाएगी।” (PMGSY Guidelines (Hindi) — पैरा 6.3 (page 13))

### pm-05 — ✓ facts · ✗ cites gold
**Q:** Within what distance can the populations of nearby habitations be clubbed together to determine population size?  
**Expected:** 500 m (1.5 km path distance in hills)  
**Sources:** [1] IS 456:2000 Clause 26.3.1; [2] IS 456:2000 Clause 5.3.3 – 5.3.3.1; [3] IS 456:2000 Clause 26.3.1; [4] IS 456:2000 Clause 26.3.3 – 26.4.1; [5] PMGSY Guidelines (Hindi) पैरा 3.4–3.5; [6] PMGSY Guidelines (Hindi) पैरा 3–3.3

The populations of nearby habitations can be clubbed together within a distance of 500 meters [2]. In hilly areas, this distance is 4.5 kilometers [2].

### pm-06 — ✓ facts · ✓ cites gold
**Q:** Can PMGSY funds be used to repair black-topped or cement roads in poor condition?  
**Expected:** No, repair of black-topped or cement roads is not permitted  
**Sources:** [1] RHB BSR 2024 Item B-13.35; [2] RHB BSR 2024 Item B-13.15; [3] PMGSY Guidelines (Hindi) पैरा 3.15–3.16; [4] RHB BSR 2024 Item B-13.13; [5] PMGSY Guidelines (Hindi) पैरा 17–17.1; [6] PMGSY Guidelines (Hindi) पैरा 17.2–17.3

No, PMGSY funds cannot be used to repair black-topped or cement roads in poor condition [3]. 

Specifically, Paragraph 3.15-3.16 of the PMGSY Guidelines states: “प्रधानमंत्री ग्राम सड़क योजना में काली सतह या सीमेंट से बनी सड़कों की मरम्मत करने की अनुमति नहीं दी गई है, भले ही सतह की स्थिति खराब हो गयी हो” [3]. This translates to: “The Prime Minister’s Gram Sadak Yojana does not allow for the repair of black-surfaced or cement roads, even if the surface condition is poor” [3].

### pm-07 — ✓ facts · ✓ cites gold
**Q:** Who chairs the Empowered Committee that considers state project proposals at the centre?  
**Expected:** Secretary, Department of Rural Development  
**Sources:** [1] IS 456:2000 Annex H; [2] PMGSY Guidelines (Hindi) पैरा 8–8.2; [3] PMGSY Guidelines (Hindi) पैरा 10–10.2; [4] PMGSY Guidelines (Hindi) पैरा 9; [5] PMGSY Guidelines (Hindi) पैरा 7.5; [6] IS 456:2000 Amendment

Secretary, Rural Development Department, headed by the Rural Development Minister [3].

### pm-08 — ✓ facts · ✓ cites gold
**Q:** Explain the three-tier quality control mechanism of the rural roads programme  
**Expected:** PIU (tier 1), state quality monitors (tier 2), National Quality Monitors by NRRDA (tier 3)  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 15.2; [2] PMGSY Guidelines (Hindi) पैरा 15.5; [3] PMGSY Guidelines (Hindi) पैरा 15; [4] PMGSY Guidelines (Hindi) पृष्ठ 1; [5] PMGSY Guidelines (Hindi) पैरा 13; [6] PMGSY Guidelines (Hindi) पैरा 15.7

The PMGSY guidelines outline a three-tier quality control system for rural roads [1]. Here’s a breakdown:

*   **Tier 1:** This is managed by the Public Investment Unit (PIU). They oversee the contractor’s on-site quality control laboratory, ensuring materials and workmanship meet specifications [1]. The PIU also supervises testing conducted by designated individuals at specified times and locations [1].
*   **Tier 2:** This involves the National Rural Road Development Agency (NRRDA) conducting random inspections of road works under their program [2]. Independent monitoring personnel (either individuals or agencies) are appointed for this purpose, who can be designated as “National Quality Monitors” [2].
*   **Tier 3:** The PIU is responsible for facilitating the work of these National Quality Monitors, providing them with all administrative, technical, and financial records [2].

If repeated adverse reports regarding road quality arise in a specific district/state, the program may be suspended until the underlying issues are addressed [6].

### pm-09 — ✓ facts · ✓ cites gold
**Q:** What maintenance contract is signed along with the construction contract for PMGSY roads?  
**Expected:** 5-year maintenance contract with the same contractor, funded by the state  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 17.2–17.3; [2] PMGSY Guidelines (Hindi) पैरा 11.4; [3] PMGSY Guidelines (Hindi) पैरा 3.10–3.12; [4] PMGSY Guidelines (Hindi) पैरा 3.15–3.16; [5] PMGSY Guidelines (Hindi) पैरा 8.6; [6] PMGSY Guidelines (Hindi) पृष्ठ 1

A 5-year maintenance contract is signed with the same contractor [1].

### pm-10 — ✓ facts · ✓ cites gold
**Q:** Within how long after the financial year must accounts be audited, and by whom?  
**Expected:** Within 6 months, by a chartered accountant from a CAG-approved panel; also audited by CAG  
**Sources:** [1] RHB BSR 2024 Page M-104; [2] RHB BSR 2024 Page M-3; [3] RHB BSR 2024 Page M-105; [4] PMGSY Guidelines (Hindi) पैरा 20; [5] PMGSY Guidelines (Hindi) पैरा 12.2; [6] PMGSY Guidelines (Hindi) पैरा 19.2

Within six months after the financial year, by a chartered accountant selected from a panel approved by the Comptroller and Auditor General (CAG) [4].

### pm-11 — ✓ facts · ✓ cites gold
**Q:** प्रधानमंत्री ग्राम सड़क योजना का मुख्य उद्देश्य क्या है?  
**Expected:** Connect eligible unconnected habitations with all-weather roads (1000+ by 2003, 500+ by 2007)  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 1.2; [2] PMGSY Guidelines (Hindi) पैरा 3.13–3.14; [3] PMGSY Guidelines (Hindi) पैरा 2–2.1; [4] PMGSY Guidelines (Hindi) पृष्ठ 1; [5] PMGSY Guidelines (Hindi) पैरा 3.15–3.16; [6] PMGSY Guidelines (Hindi) पैरा 3–3.3

प्रधानमंत्री ग्राम सड़क योजना (पीएमजीएसवाई) का मुख्य उद्देश्य संपर्क विहीन पात्र बसावटों को बारहमासी सड़क संपर्क मुहैया कराना है [2]. 

*   यह कार्यक्रम 000 और अधिक की आबादी वाली बसावटों को तीन वर्षों में और 500 और इससे अधिक की आबादी वाली सड़कों से न जुड़ी सभी बसावटों को दसवीं योजना अवधि (2007) के अंत तक कवर करने का लक्ष्य रखता है [3].
*   पर्वतीय राज्यों (पूर्वोत्तर, सिक्किम, हिमाचल प्रदेश, जम्मू एवं कश्मीर, उत्तरांचल ) तथा मरूभूमि क्षेत्रों में भी 250 और इससे अधिक की आबादी वाली बसावटों को सड़कों से जोड़ना है [3].

### pm-12 — ✓ facts · ✓ cites gold
**Q:** राज्य तकनीकी एजेंसी (एसटीए) का क्या काम है?  
**Expected:** Technical support to PIUs; scrutinise DPRs, district road plans and core network  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 9.1; [2] PMGSY Guidelines (Hindi) पैरा 7–7.1; [3] PMGSY Guidelines (Hindi) पैरा 7.4; [4] PMGSY Guidelines (Hindi) पैरा 7.2; [5] PMGSY Guidelines (Hindi) पैरा 7.3; [6] PMGSY Guidelines (Hindi) पैरा 15.3

एसटीए की निम्नलिखित गतिविधियाँ हैं: [1]

*   परिवेशी सड़क योजना और कोर नेटवर्क की जांच करेगी।
*   सीएनसीपीएल और सीयूपीएल की जांच करेगी।
*   वार्षिक प्रस्तावों के अंतर्गत तैयार किए गए डीपीआर की समीक्षा करेगी।

एसटीए की गतिविधियों का समन्वय एनआरआरडीए द्वारा किया जाएगा। [1]

### pm-13 — ✓ facts · ✓ cites gold
**Q:** कार्यक्रम कार्यान्वयन इकाइयों का स्टाफ खर्च कौन वहन करता है?  
**Expected:** State Government; PMGSY provides no staff cost  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 12.2; [2] PMGSY Guidelines (Hindi) पैरा 12–12.1; [3] PMGSY Guidelines (Hindi) पैरा 12.3; [4] PMGSY Guidelines (Hindi) पैरा 12.2; [5] PMGSY Guidelines (Hindi) पैरा 12.2; [6] PMGSY Guidelines (Hindi) पैरा 7.4

राज्य सरकार [1].

### pm-14 — ✓ facts · ✓ cites gold
**Q:** बसावट की परिभाषा क्या है?  
**Expected:** A cluster of population living in an area whose location does not change over time  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 3–3.3; [2] PMGSY Guidelines (Hindi) पैरा 3.4–3.5; [3] PMGSY Guidelines (Hindi) पैरा 3.6–3.7; [4] PMGSY Guidelines (Hindi) पैरा 3.10–3.12; [5] PMGSY Guidelines (Hindi) पैरा 4.4–4.5; [6] PMGSY Guidelines (Hindi) पैरा 3.8

बसावट की परिभाषा इस प्रकार है: [1] “क्षेत्र में रहने वाली जनसंख्या के समूह, जो लंबे समय तक स्थान नहीं बदलते हैं, को बसावट कहते हैं। देशम, धानी, टोला, माजरा, हेमलेट आदि बसावटों की व्याख्या के लिए सामान्य रूप से प्रयोग में आने वाले शब्द हैं।” [2] “जनगणना 200 में दर्ज की गई जनसंख्या बसावट की जनसंख्या आकार को निर्धारित करने का आधार होनी चाहिए। जनसंख्या आकार को निर्धारित करने के प्रयोजनार्थ 500 मीटर की दूरी के भीतर (पहाड़ियों के मामले में पैदल दूरी 4.5 कि.मी) सभी बसावटों की जनसंख्या को एक साथ शामिल किया जा सकता है तथापि पहाड़ी राज्यों में अंतर्राष्ट्रीय सीमा से लगे खण्डों (गृह मंत्रालय द्वारा पहचान किए गए अनुसार) में 0 कि.मी.की पैदल दूरी में पड़ने वाली सभी बसावटों को इस उद्देश्य के लिए समूह माना जा सकता है।”

### pm-15 — ✓ facts · ✓ cites gold
**Q:** योजना की निधियों के लिए बैंक खाता कौन चुनेगा?  
**Expected:** SRRDA selects a public sector / scheduled bank branch with internet connectivity at state HQ  
**Sources:** [1] PMGSY Guidelines (Hindi) पैरा 18–18.2; [2] PMGSY Guidelines (Hindi) पैरा 18.4; [3] PMGSY Guidelines (Hindi) पैरा 18.3; [4] PMGSY Guidelines (Hindi) पैरा 18.8; [5] PMGSY Guidelines (Hindi) पैरा 18.4; [6] PMGSY Guidelines (Hindi) पैरा 18.5–18.7

एसआरआरडीए (State Rural Road Development Agency) योजना की निधियों के लिए बैंक खाता चुनेगा [1].
