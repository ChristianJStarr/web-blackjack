import {Chip} from "./chip.js";
import {arraysEqual, createElement} from "./utility.js";

export class Bank {

    constructor(table) {
        this.table = table;
        this.chips = [];
        this.balance = 0;
        this.bet = 0;

        this.node = createElement('div', 'bank');
        this.chips_node = createElement('div', 'bank__chips');

        this.balance_wrapper_node = createElement('div', 'bank__balance-wrapper');
        this.balance_node = createElement('div', 'bank__balance');
        this.balance_change_node = createElement('div', 'bank__balance-change');

        this.header_balance = document.querySelector('.header__balance');

        this.balance_wrapper_node.append(
            this.balance_node,
            this.balance_change_node
        );

        this.node.append(
            this.chips_node,
            this.balance_wrapper_node
        );

        this.debounceTimeout = null;
        this.debounceDelay = 100;
        this.pendingBetAmount = null;
    }

    updateBalance(balance) {
        this.balance_node.textContent = `$${balance}`;
        if (this.header_balance) {
            this.header_balance.textContent = `$${balance}`;
        }

        const change = balance - this.balance;
        if (this.balance && change) {
            this.balance_change_node.textContent = `${change > 0 ? '+':''}${change}`;
            this.balance_change_node.classList.add(change > 0 ? '-increase' : '-decrease');
            setTimeout(()=>{
                this.balance_change_node.classList.remove(change > 0 ? '-increase' : '-decrease');
                this.balance_change_node.textContent = ``;
            }, 1000);
        }
        this.balance = balance;
    }

    updateChips(chips) {
        for (const chip_value of chips) {
            const chip_object = new Chip(chip_value);

            chip_object.node.onclick = this.debounce(() => {
                this.pendingBetAmount += chip_value;
                this.table.sound('chip');
                this.processBet();
            }, this.debounceDelay);
            this.chips_node.append(chip_object.node)
        }
        this.chips = chips;
    }

    processBet() {
        if (this.pendingBetAmount !== null) {
            this.table.action('player_bet', this.pendingBetAmount);
            this.pendingBetAmount = null;
        }
    }

    debounce(func, delay) {
        return (...args) => {
            if (this.debounceTimeout) {
                clearTimeout(this.debounceTimeout);
            }
            this.debounceTimeout = setTimeout(() => func(...args), delay);
        };
    }

    update(state) {

        const chips = state?.chips ?? [];
        const seats = state?.seats ?? [];

        let balance = 0;
        for (const seat of seats) {
            if(this.table.game.seat_id === seat.id) {
                balance = seat.player.balance;
            }
        }

        chips.sort((a, b) => a - b);

        if(!arraysEqual(this.chips, chips)) {
            this.updateChips(chips);
        }

        if(balance !== this.balance) {
            this.updateBalance(balance);
        }
    }
}