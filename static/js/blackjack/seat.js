import {Card} from "./card.js";
import {Chip} from "./chip.js";
import {createElement} from "./utility.js";

export class Seat {
    constructor(table, seat_id) {
        this.table = table;
        this.id = seat_id;

        this.cards = [];
        this.bet = 0;
        this.player = {};
        this.hand_value = 0;
        this.active = false;
        this.self = false;
        this.card_objects = [];

        this.node = createElement('div', 'seat');
        this.cards_node = createElement('div', 'seat__cards');
        this.hand_value_node = createElement('div', 'seat__hand-value');
        this.player_node = createElement('div', 'seat__player');
        this.bet_node = createElement('div', 'seat__bet');
        this.bet_text_node = createElement('div', 'seat__bet-text');

        this.bet_center_node = createElement('div', 'seat__bet__center');
        this.bet_behind_node = createElement('div', 'seat__bet__behind');
        this.bet_side_l_node = createElement('div', 'seat__bet__side-l');
        this.bet_side_r_node = createElement('div', 'seat__bet__side-r');

        this.bet_center_bet_node = createElement('div', 'seat__bet__center__bet');
        this.bet_behind_bet_node = createElement('div', 'seat__bet__behind__bet');
        this.bet_side_l_bet_node = createElement('div', 'seat__bet__side-l__bet');
        this.bet_side_r_bet_node = createElement('div', 'seat__bet__side-r__bet');

        this.bet_center_text_node = createElement('div', 'seat__bet__center__text');
        this.bet_behind_text_node = createElement('div', 'seat__bet__behind__text');
        this.bet_side_l_text_node = createElement('div', 'seat__bet__side-l__text');
        this.bet_side_r_text_node = createElement('div', 'seat__bet__side-r__text');

        this.bet_center_text_node.textContent = 'BET';
        this.bet_behind_text_node.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 600 150">
          <path id="bet-curve" fill="none" stroke="none" d="m 131.233725,31.233725 c 0,0 61.574343,63.73891 168.766275,63.73891 121.84084,0 168.76627,-63.73891 168.76627,-63.73891"/>
          <text font-size="42" fill="#fff" letter-spacing="5" font-family="sans-serif" font-weight="bold">
            <textPath xlink:href="#bet-curve" side="left" startOffset="35">BET&nbsp;BEHIND</textPath>
          </text>
        </svg>`;
        this.bet_side_l_text_node.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 600 150"> 
          <text font-size="52" fill="#fff" letter-spacing="5" font-family="sans-serif" font-weight="bold">
          <textPath xlink:href="#bet-curve" side="left" startOffset="100">PAIRS</textPath></text>
        </svg>`;
        this.bet_side_r_text_node.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 600 150">
          <text font-size="52" fill="#fff" letter-spacing="5" font-family="sans-serif" font-weight="bold">
          <textPath xlink:href="#bet-curve" side="left" startOffset="90">21 + 3</textPath></text>
        </svg>`;

        this.bet_center_node.append(
            this.bet_center_bet_node,
            this.bet_center_text_node,
        );

        this.bet_behind_node.append(
            this.bet_behind_bet_node,
            this.bet_behind_text_node,
        );

        this.bet_side_l_node.append(
            this.bet_side_l_bet_node,
            this.bet_side_l_text_node,
        );

        this.bet_side_r_node.append(
            this.bet_side_r_bet_node,
            this.bet_side_r_text_node,
        );

        this.bet_node.append(
            this.bet_center_node,
            this.bet_side_l_node,
            this.bet_side_r_node,
            this.bet_behind_node,
        );

        this.node.append(
            this.cards_node,
            this.hand_value_node,
            this.bet_node,
            this.player_node,
            this.bet_text_node
        );
    }

    update(state) {
        try {
            const cards = state?.cards ?? [];
            const bet = state?.bet ?? 0;
            const player = state?.player ?? {};
            const hand_value = state?.hand_value ?? 0;
            const active = state?.active ?? false;
            const self = state?.self ?? false;

            if(cards !== this.cards) {
                this.setCards(cards);
            }
            if (bet !== this.bet) {
                this.setBet(bet);
            }
            if(player !== this.player) {
                this.setPlayer(player);
            }
            if(hand_value !== this.hand_value) {
                this.setHandValue(hand_value);
            }
            if (active !== this.active) {
                this.setActive(active);
            }
            if (self !== this.self) {
                this.setSelf(self);
            }
        }
        catch (err) {
            console.error(`Failed to update seat ID ${this.id}`, err);
        }
    }
    setSelf(self) {
        if(self) {
            this.node.classList.add('-self');
        }else{
            this.node.classList.remove('-self');
        }
        this.self = self;
    }
    setActive(active) {
        if(active) {
            this.node.classList.add('-active');
        }else{
            this.node.classList.remove('-active');
        }
        this.active = active;
    }
    setCards(cards) {
        if (cards?.length) {
            for (const [index, card] of cards.entries()) {
                if (this.cards[index]) {
                    if(this.cards[index] !== card) {
                        this.card_objects[index].reset(card);
                        this.table.sound('card');
                    }
                } else {
                    const card_object = new Card(card);
                    this.cards_node.appendChild(card_object.node);
                    this.card_objects.push(card_object);
                    this.table.sound('card');
                }
            }
        } else {
            this.cards_node.replaceChildren();
            this.card_objects = [];
        }
        this.cards = cards;
    }
    setHandValue(hand_value) {
        if(hand_value) {
            this.hand_value_node.textContent = hand_value;
        }
        else {
            this.hand_value_node.textContent = '';
        }
        this.hand_value = hand_value;
    }
    setBet(bet) {
        if (bet) {
            const chips = this.table?.chips ?? [];
            this.bet_text_node.textContent = `$${bet}`;
            let count = bet;
            chips.sort((a, b) => b - a);

            while (count > 0) {
                let chipAdded = false;
                for (const chip_size of chips) {
                    if (chip_size <= count) {
                        count -= chip_size;
                        const chip_object = new Chip(chip_size);
                        this.bet_center_bet_node.appendChild(chip_object.node);
                        chipAdded = true;
                        break; // Break after adding a chip to avoid unnecessary checks
                    }
                }
                if (!chipAdded) {
                    // This means no chip could be added, prevent infinite loop
                    break;
                }
            }
            this.organizeChips();
        } else {
            this.bet_center_bet_node.replaceChildren();
            this.bet_text_node.textContent = '';
        }
        this.bet = bet;
    }
    setPlayer(player) {
        if(player?.id) {
            this.player_node.textContent = player.name;
        }
        this.player = player;
    }
    organizeChips() {
        const groups = {};
        for (const chip of this.bet_center_bet_node.children) {
            const chip_value = chip.dataset.value;
            if (!Array.isArray(groups[chip_value])) {
                groups[chip_value] = [];
            }
            chip.style.top = `-${groups[chip_value].length * 4}px`;
            groups[chip_value].push(chip);
        }
        const group_nodes = [];
        for (const [chip_value, items] of Object.entries(groups)) {
            const group_node = createElement('div', 'chip-group');
            group_node.dataset.value = chip_value;
            group_node.append(...items);
            group_nodes.push(group_node);
        }
        this.bet_center_bet_node.replaceChildren(...group_nodes)
    }

}