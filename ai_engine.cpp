#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <tuple>
#include <unordered_map>
#include <algorithm>
#include <limits>
#include <iostream>

using namespace std;
namespace py = pybind11;

const int NORMAL = 0;
const int REBIRTH = 14;
const int HAPPY = 25;
const int WATER = 26;
const int TRIPLE = 27;
const int DOUBLE = 28;
const int HORUS = 29;

const vector<int> board = {
    NORMAL, NORMAL, NORMAL, NORMAL, NORMAL, NORMAL, NORMAL, NORMAL, NORMAL, NORMAL,
    NORMAL, NORMAL, NORMAL, NORMAL, REBIRTH, NORMAL, NORMAL, NORMAL, NORMAL, NORMAL,
    NORMAL, NORMAL, NORMAL, NORMAL, NORMAL, HAPPY, WATER, TRIPLE, DOUBLE, HORUS
};

struct GameState {
    vector<int> player_1_rocks_pos;
    vector<int> player_2_rocks_pos;
    int current_player;

    GameState(const vector<int>& p1_pos, const vector<int>& p2_pos, int player)
        : player_1_rocks_pos(p1_pos), player_2_rocks_pos(p2_pos), current_player(player) {}

    bool is_terminal() const {
        return player_1_rocks_pos.empty() || player_2_rocks_pos.empty();
    }

    int winner() const {
        if (player_1_rocks_pos.empty()) return 1;
        if (player_2_rocks_pos.empty()) return 2;
        return 0;
    }

    size_t hash() const {
        size_t h = 0;
        for (int pos : player_1_rocks_pos) h ^= std::hash<int>{}(pos) + 0x9e3779b9 + (h << 6) + (h >> 2);
        for (int pos : player_2_rocks_pos) h ^= std::hash<int>{}(pos) + 0x9e3779b9 + (h << 6) + (h >> 2);
        h ^= std::hash<int>{}(current_player) + 0x9e3779b9 + (h << 6) + (h >> 2);
        return h;
    }
};

class TranspositionTable {
private:
    struct Entry {
        int depth;
        double value;
        Entry() : depth(0), value(0.0) {}
        Entry(int d, double v) : depth(d), value(v) {}
    };
    unordered_map<size_t, Entry> table;

public:
    bool check(const GameState& state, int depth, double& value) {
        auto it = table.find(state.hash());
        if (it != table.end() && it->second.depth >= depth) {
            value = it->second.value;
            return true;
        }
        return false;
    }

    void store(const GameState& state, int depth, double value) {
        table[state.hash()] = Entry(depth, value);
    }

    void clear() {
        table.clear();
    }
};

struct Stats {
    int nodes_visited = 0;
    int pruned_count = 0;
    void visit() { nodes_visited++; }
    void pruned() { pruned_count++; }
};

vector<pair<int, int>> available_moves(const GameState& state, int steps) {
    vector<pair<int, int>> moves;
    const auto& player_rocks_pos = (state.current_player == 1) ? 
        state.player_1_rocks_pos : state.player_2_rocks_pos;

    vector<bool> player_rocks(board.size(), false);
    for (int pos : player_rocks_pos) player_rocks[pos] = true;

    for (int pos : player_rocks_pos) {
        int new_pos = pos + steps;
        int current_cell = board[pos];

        if (current_cell == TRIPLE && steps != 3) continue;
        if (current_cell == DOUBLE && steps != 2) continue;
        if (pos < HAPPY && new_pos > HAPPY) continue;

        if (new_pos >= static_cast<int>(board.size())) {
            moves.push_back({pos, new_pos});
            continue;
        }

        if (player_rocks[new_pos]) continue;
        moves.push_back({pos, new_pos});
    }

    return moves;
}

GameState apply_move(const GameState& state, const pair<int, int>& move) {
    int old_pos = move.first;
    int new_pos = move.second;

    vector<int> p1_pos = state.player_1_rocks_pos;
    vector<int> p2_pos = state.player_2_rocks_pos;

    auto& rocks_pos = (state.current_player == 1) ? p1_pos : p2_pos;
    auto& opp_pos = (state.current_player == 1) ? p2_pos : p1_pos;

    vector<bool> opp_bool(board.size(), false);
    for (int pos : opp_pos) opp_bool[pos] = true;

    auto it = find(rocks_pos.begin(), rocks_pos.end(), old_pos);
    int rock_idx = distance(rocks_pos.begin(), it);

    if (new_pos < static_cast<int>(board.size()) && opp_bool[new_pos]) {
        auto opp_it = find(opp_pos.begin(), opp_pos.end(), new_pos);
        *opp_it = old_pos;
    }

    if (new_pos >= static_cast<int>(board.size())) {
        rocks_pos.erase(it);
        rock_idx = -1;
    } else {
        *it = new_pos;
    }

    vector<bool> combined_pos(board.size(), false);
    for (int pos : p1_pos) combined_pos[pos] = true;
    for (int pos : p2_pos) combined_pos[pos] = true;

    for (size_t i = 0; i < rocks_pos.size(); i++) {
        int pos = rocks_pos[i];
        if (board[pos] == WATER || 
            ((board[pos] == DOUBLE || board[pos] == TRIPLE || board[pos] == HORUS) && 
             static_cast<int>(i) != rock_idx)) {
            
            int target = REBIRTH;
            while (combined_pos[target]) {
                target--;
                if (target < 0) {
                    target = 0;
                    break;
                }
            }
            rocks_pos[i] = target;
        }
    }

    int next_player = (state.current_player == 1) ? 2 : 1;
    return GameState(p1_pos, p2_pos, next_player);
}

double evaluate_state(const GameState& state, int player) {
    if (state.is_terminal()) {
        int winner = state.winner();
        if (winner == player) return 10000.0;
        if (winner != 0) return -10000.0;
        return 0.0;
    }

    const auto& p_positions = (player == 1) ? state.player_1_rocks_pos : state.player_2_rocks_pos;
    const auto& o_positions = (player == 1) ? state.player_2_rocks_pos : state.player_1_rocks_pos;

    int player_pieces = p_positions.size();
    int opponent_pieces = o_positions.size();

    double player_advancement = 0.0;
    if (player_pieces > 0) {
        for (int pos : p_positions) player_advancement += pos;
        player_advancement /= player_pieces;
    }

    double opponent_advancement = 0.0;
    if (opponent_pieces > 0) {
        for (int pos : o_positions) opponent_advancement += pos;
        opponent_advancement /= opponent_pieces;
    }

    double piece_advantage = (opponent_pieces - player_pieces) * 10.0;
    double advancement_advantage = (player_advancement - opponent_advancement) * 0.5;

    int p_happy = 0, o_happy = 0;
    for (int pos : p_positions) if (pos > HAPPY) p_happy++;
    for (int pos : o_positions) if (pos > HAPPY) o_happy++;
    double happy_bonus = (p_happy - o_happy) * 5.0;

    int p_risky = 0, o_risky = 0;
    for (int pos : p_positions) if (pos < static_cast<int>(board.size()) && board[pos] == WATER) p_risky++;
    for (int pos : o_positions) if (pos < static_cast<int>(board.size()) && board[pos] == WATER) o_risky++;
    double risky_penalty = (o_risky - p_risky) * 3.0;

    int p_exit = 0, o_exit = 0;
    for (int pos : p_positions) if (pos > 20) p_exit += (pos - 20);
    for (int pos : o_positions) if (pos > 20) o_exit += (pos - 20);
    double exit_bonus = (p_exit - o_exit) * 0.2;

    double score = piece_advantage + advancement_advantage + happy_bonus + risky_penalty + exit_bonus;

    if (player_pieces <= 2 && opponent_pieces <= 2) {
        score += (player_advancement - opponent_advancement) * 0.15;
    }

    return score;
}

unordered_map<int, double> get_dice_probabilities() {
    return {{1, 4.0/16}, {2, 6.0/16}, {3, 4.0/16}, {4, 1.0/16}, {5, 1.0/16}};
}

double expectiminimax(const GameState& state, int depth, int player, Stats& stats,
                     double alpha, double beta, TranspositionTable& tt) {
    stats.visit();

    double cached_value;
    if (tt.check(state, depth, cached_value)) {
        return cached_value;
    }

    if (depth == 0 || state.is_terminal()) {
        double eval = evaluate_state(state, player);
        tt.store(state, depth, eval);
        return eval;
    }

    double total_expected_value = 0.0;
    auto probabilities = get_dice_probabilities();

    for (const auto& [roll, prob] : probabilities) {
        auto moves = available_moves(state, roll);
        double outcome_value;

        if (moves.empty()) {
            int next_player = (state.current_player == 1) ? 2 : 1;
            GameState next_state(state.player_1_rocks_pos, state.player_2_rocks_pos, next_player);
            outcome_value = expectiminimax(next_state, depth - 1, player, stats, alpha, beta, tt);
        } else {
            vector<pair<pair<int, int>, double>> moves_with_scores;
            moves_with_scores.reserve(moves.size());
            
            for (const auto& m : moves) {
                GameState new_state = apply_move(state, m);
                double score = evaluate_state(new_state, player);
                moves_with_scores.push_back({m, score});
            }

            if (state.current_player == player) {
                sort(moves_with_scores.begin(), moves_with_scores.end(),
                     [](const auto& a, const auto& b) { return a.second > b.second; });
                
                double best_value = -numeric_limits<double>::infinity();
                double local_alpha = alpha;

                for (const auto& [move, _] : moves_with_scores) {
                    GameState new_state = apply_move(state, move);
                    double cv = expectiminimax(new_state, depth - 1, player, stats, 
                                               local_alpha, beta, tt);
                    
                    best_value = max(best_value, cv);
                    local_alpha = max(local_alpha, cv);
                    
                    if (local_alpha >= beta) {
                        stats.pruned();
                        break;
                    }
                }
                
                outcome_value = best_value;
            } else {
                sort(moves_with_scores.begin(), moves_with_scores.end(),
                     [](const auto& a, const auto& b) { return a.second < b.second; });
                
                double best_value = numeric_limits<double>::infinity();
                double local_beta = beta;

                for (const auto& [move, _] : moves_with_scores) {
                    GameState new_state = apply_move(state, move);
                    double cv = expectiminimax(new_state, depth - 1, player, stats, 
                                               alpha, local_beta, tt);
                    
                    best_value = min(best_value, cv);
                    local_beta = min(local_beta, cv);
                    
                    if (alpha >= local_beta) {
                        stats.pruned();
                        break;
                    }
                }
                
                outcome_value = best_value;
            }
        }

        total_expected_value += prob * outcome_value;
        
                if (stats.nodes_visited % 100000 == 0)

        cout << "Nodes: " << stats.nodes_visited 
         << " | Pruned: " << stats.pruned_count << endl;
    }

    tt.store(state, depth, total_expected_value);
    return total_expected_value;
}

tuple<pair<int, int>, int, double> get_best_move(
    const vector<int>& p1_pos,
    const vector<int>& p2_pos,
    int current_player,
    int roll,
    int depth) {

    GameState state(p1_pos, p2_pos, current_player);
    auto moves = available_moves(state, roll);

    if (moves.empty()) {
        return {{-1, -1}, 0, 0.0};
    }

    Stats stats;
    TranspositionTable tt;

    pair<int, int> best_move = moves[0];
    double best_score = -numeric_limits<double>::infinity();

    for (const auto& move : moves) {
        GameState next_state = apply_move(state, move);
        double score = expectiminimax(next_state, depth - 1, current_player, stats,
                                     -numeric_limits<double>::infinity(),
                                     numeric_limits<double>::infinity(), tt);

        if (score > best_score) {
            best_score = score;
            best_move = move;
        }
    }
    
    cout << "Nodes: " << stats.nodes_visited 
         << " | Score: " << best_score 
         << " | Pruned: " << stats.pruned_count << endl;
    
    return {best_move, stats.nodes_visited, best_score};
}

PYBIND11_MODULE(ai_cpp, m) {
    m.doc() = "C++ AI with CORRECT Expectiminimax";
    
    m.def("get_best_move", &get_best_move,
          py::arg("p1_pos"),
          py::arg("p2_pos"),
          py::arg("current_player"),
          py::arg("roll"),
          py::arg("depth"));
}