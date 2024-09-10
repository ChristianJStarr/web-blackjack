import {Seat} from "./seat.js";
import {createElement} from "./utility.js";

export class Seats {

    constructor(table, count=6) {
        this.table = table;
        this.node = createElement('div', 'seats');

        this.seats = Object.fromEntries(Array.from({ length: count },
            (_, id) => [id+1, new Seat(table, id+1)]
        ));

        for (const seat of Object.values(this.seats)) {
            this.node.append(seat.node);
        }
    }

    update(state) {
        const self_seat = this.table.game.seat_id;
        const active_seat = state?.turn ?? 0;
        const seats_state = state?.seats ? state.seats : [];
        for (const seat_state of seats_state) {
            const seat_id = seat_state.id;
            if (seat_id) {
                for (const seat of Object.values(this.seats)) {
                    if (seat.id === seat_id) {
                        seat.update({ active: seat_id === active_seat, self: seat_id === self_seat, ...seat_state });
                    }
                }
            }
        }
    }
}