# ADL3

## Example CLI usage

```
cat > lib.adl3 <<EOF
Load releases loaded during 2
Load releases ~hidden during 1
Shoot causes ~loaded during 1
Shoot causes ~alive if loaded & ~hidden during 1
impossible Shoot if ~loaded
EOF

cat > scenario.txt <<EOF
OBS:
0 alive & ~loaded & hidden
2 alive & ~loaded & ~hidden
ACS:
Load 1 2
Shoot 3 1
EOF

cat > queries.txt <<EOF
necessary executable load,shoot in 3
possibly executable shoot in 0
possibly executable shoot in 1
possibly executable shoot in 2
necessary alive & ~loaded at 0 when scenario.txt
necessary alive & ~loaded at -1 when scenario.txt
possibly hidden at 2 when scenario.txt
necessary ~hidden at 3 when scenario.txt
possibly ~loaded & ~alive at 4 when scenario.txt
necessary ~loaded & ~alive at 4 when scenario.txt
EOF

$ ./main.py -l lib.txt -s scenario.txt -q queries.txt
Query: necessary executable load,shoot in 3 was evaluated to: True
Query: possibly executable shoot in 1 was evaluated to: True
Query: possibly executable shoot in 2 was evaluated to: True
Query: necessary alive & ~loaded at 0 when scenario.txt was evaluated to: True
Query: possibly hidden at 2 when scenario.txt was evaluated to: False
Query: necessary ~hidden at 3 when scenario.txt was evaluated to: True
Query: possibly ~alive & ~loaded at 4 when scenario.txt was evaluated to: True
Query: necessary ~alive & ~loaded at 4 when scenario.txt was evaluated to: True
```

## Running unit tests

```
python3.6 -m unittest
```
