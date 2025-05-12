import {createElement} from "./utility.js";
import {Card} from "./card.js";

export class Dealer {

    constructor(table) {
        this.table = table;
        this.cards = [];
        this.card_objects = [];
        this.hand_value = 0;
        this.checking = false;

        this.node = createElement('div', 'dealer');
        this.cards_node = createElement('div', 'dealer__cards');
        this.hand_value_node = createElement('div', 'dealer__hand-value');
        this.pays_node = createElement('div', 'dealer__pays');

        this.pays_node.textContent = 'BLACKJACK PAYS 3 TO 2';

        this.node.append(
            this.cards_node,
            this.hand_value_node,
            this.pays_node
        )
    }

    update(state) {
        const cards = state?.dealer?.cards ?? [];
        const hand_value = state?.dealer?.hand_value ?? 0;
        const checking = state?.dealer?.checking ?? false;

        if(cards !== this.cards) {
            this.setCards(cards);
        }
        if(hand_value !== this.hand_value) {
            this.setHandValue(hand_value);
        }
        if(checking !== this.checking) {
            this.setChecking(checking);
        }
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
    setChecking(checking) {
        if(this.cards) {
            for (const [index, card] of this.cards.entries()) {
                const card_object = this.card_objects[index];
                if(card && card.includes('B') && card_object) {
                    if (checking) {
                        card_object.node.classList.add('-checking');
                    }
                    else {
                        card_object.node.classList.remove('-checking');
                    }
                }
            }
        }
        this.checking = checking;
    }
}