import {createElement} from "./utility.js";

export class Shoe {

    constructor(table=null, type) {
        this.table = table;
        this.node = createElement('div', 'shoe');
        this.cards_node = createElement('div', 'shoe__cards');
        this.text_node = createElement('p', 'shoe__label');

        this.text_node.textContent = `Shoe`;

        this.cards = [];

        this.node.append(
            this.text_node,
            this.cards_node,
        )
    }


    update(state) {
        const cards = state?.shoe?.cards ?? [];
        const card_count = state?.shoe?.card_count ?? 0;

        if(cards !== this.cards) {
            this.setCards(cards);
        }
        if(card_count !== this.card_count) {
            this.setLabel(card_count)
        }
    }


    setCards(cards) {
        if(cards) {
            this.cards_node.replaceChildren();
            for (const [index, card] of cards.entries()) {
                const card_node = createElement('div', `shoe__card`);

                if(index === cards.length - 20) {
                    card_node.classList.add('-cut')
                }

                this.cards_node.append(card_node);
            }
        }else {
            this.cards_node.replaceChildren();
        }
        this.cards = cards;
    }

    setLabel(card_count) {
        if(card_count) {
            this.text_node.textContent = `Shoe (${card_count} cards)`;
        }else {
            this.text_node.textContent = `Shoe`;
        }
        this.card_count = card_count;
    }
}