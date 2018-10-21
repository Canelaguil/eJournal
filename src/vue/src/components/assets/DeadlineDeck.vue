<template>
    <div>
        <!-- TODO: This seems like an inappropriate permission check. Will have to be reconsidered in the rework. -->
        <b-card v-if="$hasPermission('can_add_course')" class="no-hover">
            <b-form-select v-model="selectedSortOption" :select-size="1">
                <option value="sortDate">Sort by date</option>
                <option value="sortNeedsMarking">Sort by marking needed</option>
            </b-form-select>
        </b-card>

        <div v-for="(d, i) in computedDeadlines" :key="i">
            <b-link tag="b-button" :to="assignmentRoute(d.course.id, d.id, d.journal)">
                <todo-card :deadline="d"/>
            </b-link>
        </div>
    </div>
</template>

<script>
import todoCard from '@/components/assets/TodoCard.vue'
import todoSquare from '@/components/assets/TodoSquare.vue'

export default {
    props: ['deadlines'],
    data () {
        return {
            selectedSortOption: 'sortDate'
        }
    },
    components: {
        'todo-card': todoCard,
        'todo-square': todoSquare
    },
    methods: {
        assignmentRoute (cID, aID, jID) {
            var route = {
                params: {
                    cID: cID,
                    aID: aID
                }
            }

            if (this.$hasPermission('can_view_all_journals', 'assignment', String(aID))) {
                route.name = 'Assignment'
                return route
            }
            route.name = 'Journal'
            route.params.jID = jID
            return route
        }
    },
    computed: {
        computedDeadlines: function () {
            var counter = 0
            function compareDate (a, b) {
                return new Date(a.deadline) - new Date(b.deadline)
            }

            function compareMarkingNeeded (a, b) {
                if (a.stats.needs_marking + a.stats.unpublished > b.stats.needs_marking + b.stats.unpublished) { return -1 }
                if (a.stats.needs_marking + a.stats.unpublished < b.stats.needs_marking + b.stats.unpublished) { return 1 }
                return 0
            }

            function filterTop () {
                return (++counter <= 5)
            }

            function filterNoEntries (deadline) {
                return deadline.totalNeedsMarking !== 0
            }

            if (this.selectedSortOption === 'sortDate') {
                return this.deadlines.slice().sort(compareDate).filter(filterTop)
            } else if (this.selectedSortOption === 'sortNeedsMarking') {
                return this.deadlines.slice().sort(compareMarkingNeeded).filter(filterTop).filter(filterNoEntries)
            } else {
                return this.deadlines.slice().sort(compareDate).filter(filterTop)
            }
        }
    }
}
</script>
