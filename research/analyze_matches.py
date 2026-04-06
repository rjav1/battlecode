import json
import sys
from collections import defaultdict

with open('C:/Users/rahil/downloads/battlecode/research/match_data.json') as f:
    raw = json.load(f)

team_id = 'd26cf1d1-efc6-45d2-ac75-bfba4ce4aadc'

matches = []
for entry in raw:
    m = entry['match']
    games = entry['games']

    we_are_a = m['teamAId'] == team_id
    opponent = m['teamBName'] if we_are_a else m['teamAName']
    opponent_id = m['teamBId'] if we_are_a else m['teamAId']
    our_score = m['scoreA'] if we_are_a else m['scoreB']
    their_score = m['scoreB'] if we_are_a else m['scoreA']
    we_won = m.get('winnerId') == team_id

    game_details = []
    for g in games:
        we_won_game = g['winnerId'] == team_id
        game_details.append({
            'map': g['mapName'],
            'turns': g['turnsPlayed'],
            'win_condition': g['winCondition'],
            'we_won': we_won_game,
        })

    matches.append({
        'opponent': opponent,
        'opponent_id': opponent_id,
        'our_score': our_score,
        'their_score': their_score,
        'we_won': we_won,
        'games': game_details,
    })

# Overall stats
total = len(matches)
wins = sum(1 for m in matches if m['we_won'])
losses = total - wins
print(f'=== OVERALL: {wins}W-{losses}L out of {total} matches ({100*wins/total:.0f}% WR) ===')
print()

# Per-opponent stats
opponent_stats = defaultdict(lambda: {'our_wins': 0, 'our_losses': 0, 'games': []})
for m in matches:
    opp = m['opponent']
    if m['we_won']:
        opponent_stats[opp]['our_wins'] += 1
    else:
        opponent_stats[opp]['our_losses'] += 1
    opponent_stats[opp]['games'].extend(m['games'])

# Win condition analysis across all games
all_games = []
for m in matches:
    for g in m['games']:
        gc = dict(g)
        gc['opponent'] = m['opponent']
        all_games.append(gc)

total_games = len(all_games)
print(f'Total individual games: {total_games}')

wc_counts = defaultdict(int)
wc_our_wins = defaultdict(int)
for g in all_games:
    wc_counts[g['win_condition']] += 1
    if g['we_won']:
        wc_our_wins[g['win_condition']] += 1

print()
print('=== WIN CONDITIONS ===')
for wc, count in sorted(wc_counts.items(), key=lambda x: -x[1]):
    our_w = wc_our_wins[wc]
    print(f'  {wc}: {count} games, we won {our_w} ({100*our_w/count:.0f}%)')

# Analyze each opponent
print()
print('=== OPPONENT ANALYSIS ===')

opponent_profiles = {}
for opp, stats in sorted(opponent_stats.items(), key=lambda x: -(x[1]['our_wins']+x[1]['our_losses'])):
    games = stats['games']
    total_g = len(games)

    opp_win_games = [g for g in games if not g['we_won']]
    our_win_games = [g for g in games if g['we_won']]

    opp_core_kills = sum(1 for g in opp_win_games if g['win_condition'] == 'core_destroyed')
    opp_resource_wins = sum(1 for g in opp_win_games if g['win_condition'] == 'resources')
    opp_early_kills = sum(1 for g in opp_win_games if g['win_condition'] == 'core_destroyed' and g['turns'] < 400)
    opp_mid_kills = sum(1 for g in opp_win_games if g['win_condition'] == 'core_destroyed' and 400 <= g['turns'] < 1000)
    opp_late_kills = sum(1 for g in opp_win_games if g['win_condition'] == 'core_destroyed' and g['turns'] >= 1000)

    our_core_kills = sum(1 for g in our_win_games if g['win_condition'] == 'core_destroyed')
    our_resource_wins = sum(1 for g in our_win_games if g['win_condition'] == 'resources')

    avg_turns = sum(g['turns'] for g in games) / total_g if total_g > 0 else 0
    avg_opp_win_turns = sum(g['turns'] for g in opp_win_games) / len(opp_win_games) if opp_win_games else 0

    # Classify strategy
    if len(opp_win_games) == 0:
        strategy = 'Weaker'
    elif opp_early_kills > 0:
        strategy = 'Rush'
    elif opp_core_kills > 0 and opp_core_kills >= opp_resource_wins:
        if avg_opp_win_turns < 800:
            strategy = 'Rush'
        else:
            strategy = 'Dual'
    elif opp_core_kills > 0 and opp_resource_wins > opp_core_kills:
        strategy = 'Dual'
    elif opp_resource_wins > 0 and opp_core_kills == 0:
        strategy = 'Pure Economy'
    else:
        strategy = 'Unknown'

    opponent_profiles[opp] = {
        'strategy': strategy,
        'total_matches': stats['our_wins'] + stats['our_losses'],
        'our_wins': stats['our_wins'],
        'our_losses': stats['our_losses'],
        'opp_core_kills': opp_core_kills,
        'opp_resource_wins': opp_resource_wins,
        'opp_early_kills': opp_early_kills,
        'opp_mid_kills': opp_mid_kills,
        'opp_late_kills': opp_late_kills,
        'our_core_kills': our_core_kills,
        'our_resource_wins': our_resource_wins,
        'avg_turns': avg_turns,
        'avg_opp_win_turns': avg_opp_win_turns,
        'maps_lost': [g['map'] for g in opp_win_games],
        'maps_won': [g['map'] for g in our_win_games],
    }

    ow = stats['our_wins']
    ol = stats['our_losses']
    print(f'{opp}: {ow}W-{ol}L | Strategy: {strategy} | Avg turns: {avg_turns:.0f} | Their core kills: {opp_core_kills} (early:{opp_early_kills} mid:{opp_mid_kills} late:{opp_late_kills}) | Their resource wins: {opp_resource_wins} | Our core kills: {our_core_kills}')

# Strategy distribution
print()
print('=== STRATEGY DISTRIBUTION ===')
strat_data = defaultdict(lambda: {'opponents': [], 'total_matches': 0, 'our_wins': 0, 'our_losses': 0})
for opp, prof in opponent_profiles.items():
    s = prof['strategy']
    strat_data[s]['opponents'].append(opp)
    strat_data[s]['total_matches'] += prof['total_matches']
    strat_data[s]['our_wins'] += prof['our_wins']
    strat_data[s]['our_losses'] += prof['our_losses']

for s, data in sorted(strat_data.items(), key=lambda x: -x[1]['total_matches']):
    ow = data['our_wins']
    ol = data['our_losses']
    tm = data['total_matches']
    wr = 100*ow/tm if tm > 0 else 0
    print(f'{s}: {len(data["opponents"])} unique opponents, {tm} matches, {ow}W-{ol}L ({wr:.0f}% WR)')
    for o in data['opponents']:
        p = opponent_profiles[o]
        print(f'  - {o}: {p["our_wins"]}W-{p["our_losses"]}L')

# Maps analysis
print()
print('=== MAP ANALYSIS (sorted by our win rate) ===')
map_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'core_kills_by': 0, 'core_kills_us': 0, 'avg_turns': []})
for g in all_games:
    mp = g['map']
    if g['we_won']:
        map_stats[mp]['wins'] += 1
    else:
        map_stats[mp]['losses'] += 1
    if g['win_condition'] == 'core_destroyed':
        if g['we_won']:
            map_stats[mp]['core_kills_us'] += 1
        else:
            map_stats[mp]['core_kills_by'] += 1
    map_stats[mp]['avg_turns'].append(g['turns'])

for mp, s in sorted(map_stats.items(), key=lambda x: x[1]['wins']/(x[1]['wins']+x[1]['losses']) if (x[1]['wins']+x[1]['losses']) > 0 else 0):
    t = s['wins'] + s['losses']
    wr = 100*s['wins']/t if t > 0 else 0
    avg_t = sum(s['avg_turns'])/len(s['avg_turns'])
    print(f'{mp}: {s["wins"]}W-{s["losses"]}L ({wr:.0f}%) | Core kills: us={s["core_kills_us"]} them={s["core_kills_by"]} | Avg turns: {avg_t:.0f}')

# Core destruction analysis
print()
print('=== CORE DESTRUCTION DETAILS ===')
core_games = [g for g in all_games if g['win_condition'] == 'core_destroyed']
print(f'Total core destruction games: {len(core_games)}')
our_core_wins = [g for g in core_games if g['we_won']]
their_core_wins = [g for g in core_games if not g['we_won']]
print(f'  We destroyed their core: {len(our_core_wins)} times')
print(f'  They destroyed our core: {len(their_core_wins)} times')

if their_core_wins:
    print()
    print('Games where our core was destroyed:')
    for g in sorted(their_core_wins, key=lambda x: x['turns']):
        print(f'  Round {g["turns"]} on {g["map"]} by {g["opponent"]}')

# Close match analysis
print()
print('=== CLOSE MATCHES (3-2) ===')
close_matches = [m for m in matches if abs(m['our_score'] - m['their_score']) == 1]
close_wins = sum(1 for m in close_matches if m['we_won'])
close_losses = len(close_matches) - close_wins
print(f'Close matches: {len(close_matches)} total, {close_wins}W-{close_losses}L')

# Blowout analysis
print()
print('=== BLOWOUT MATCHES (4-1 or 5-0) ===')
blowout_matches = [m for m in matches if abs(m['our_score'] - m['their_score']) >= 3]
blowout_wins = sum(1 for m in blowout_matches if m['we_won'])
blowout_losses = len(blowout_matches) - blowout_wins
print(f'Blowout matches: {len(blowout_matches)} total, {blowout_wins}W-{blowout_losses}L')
print('Blowout losses:')
for m in blowout_matches:
    if not m['we_won']:
        print(f'  vs {m["opponent"]}: {m["our_score"]}-{m["their_score"]}')
        for g in m['games']:
            print(f'    Game on {g["map"]}: {g["win_condition"]} at turn {g["turns"]} ({"W" if g["we_won"] else "L"})')
