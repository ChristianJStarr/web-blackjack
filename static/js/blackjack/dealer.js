import {createElement} from "./utility.js";
import {Card} from "./card.js";

export class Dealer {

    constructor(table) {
        this.table = table;
        this.cards = [];
        this.card_objects = [];

        this.node = createElement('div', 'dealer');
        this.cards_node = createElement('div', 'cards');

        this.node.appendChild(this.cards_node);
    }

    update(state) {
        const cards = state?.dealer?.cards ?? [];
        if(cards !== this.cards) {
            this.setCards(cards);
        }
    }
    setCards(cards) {
        if (cards) {
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
}