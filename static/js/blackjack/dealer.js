import {createElement} from "./utility.js";
import {Card} from "./card.js";

export class Dealer {

    constructor(table) {
        this.table = table;
        this.cards = [];
        this.card_objects = [];
        this.hand_value = 0;

        this.node = createElement('div', 'dealer');
        this.cards_node = createElement('div', 'dealer__cards');
        this.hand_value_node = createElement('div', 'dealer__hand-value');

        this.node.append(
            this.cards_node,
            this.hand_value_node
        )
    }

    update(state) {
        const cards = state?.dealer?.cards ?? [];
        const hand_value = state?.dealer?.hand_value ?? 0;

        if(cards !== this.cards) {
            this.setCards(cards);
        }
        if(hand_value !== this.hand_value) {
            this.setHandValue(hand_value);
        }
    }
    setCards(cards) {
        if (cards?.length) {
            for (const [index, card] of cards.entries()) {
                if (this.cards[index]) {
                    if(this.cards[index] !== card) {
                        this.card_objects[index].reset(card);
                    }
                } else {
                    const card_object = new Card(card);
                    this.cards_node.appendChild(card_object.node);
                    this.card_objects.push(card_object);
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
}