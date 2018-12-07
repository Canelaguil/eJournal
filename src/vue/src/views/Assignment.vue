<!-- TODO Is this check really required if we redirect, or even better have correct flow anyway? -->
<template v-if="$hasPermission('can_view_all_journals')">
    <content-columns>
        <bread-crumb slot="main-content-column" @edit-click="handleEdit()"/>
        <b-card slot="main-content-column" class="no-hover settings-card">
            <input class="theme-input full-width multi-form" type="text" v-model="searchVariable" placeholder="Search..."/>
            <div class="d-flex">
                <b-form-select class="multi-form mr-2" v-model="selectedFilterGroupOption"
                               :select-size="1">
                    <option :value="null">Filter group by ...</option>
                    <option v-for="group in groups" :key="group.name" :value="group.name">
                        {{ group.name }}
                    </option>
                </b-form-select>
                <b-form-select class="multi-form mr-2" v-model="selectedSortOption" :select-size="1">
                   <option value="sortFullName">Sort by name</option>
                   <option value="sortUsername">Sort by username</option>
                   <option value="sortMarking">Sort by marking needed</option>
                </b-form-select>
                <b-button v-on:click.stop v-if="!order" @click="toggleOrder" class="button multi-form">
                    <icon name="long-arrow-down"/>
                    Ascending
                </b-button>
                <b-button v-on:click.stop v-if="order" @click="toggleOrder" class="button multi-form">
                    <icon name="long-arrow-up"/>
                    Descending
                </b-button>
            </div>
            <b-button
                v-if="$hasPermission('can_publish_grades') && assignmentJournals.length > 0"
                class="add-button full-width"
                @click="publishGradesAssignment">
                <icon name="upload"/>
                Publish all Grades for this Assignment
            </b-button>
        </b-card>

        <div v-if="filteredJournals" v-for="journal in filteredJournals" :key="journal.student.id" slot="main-content-column">
            <b-link tag="b-button" :to="{ name: 'Journal',
                                          params: {
                                              cID: cID,
                                              aID: aID,
                                              jID: journal.id
                                          }, query: query
                                        }">

                <student-card
                    :student="journal.student"
                    :stats="journal.stats">
                </student-card>
            </b-link>
        </div>
        <main-card v-if="loadingJournals && assignmentJournals.length === 0" slot="main-content-column" class="no-hover" :line1="'Loading journals...'"/>
        <main-card v-else-if="assignmentJournals.length === 0" slot="main-content-column" class="no-hover" :line1="'No participants with a journal'"/>
        <main-card v-else-if="filteredJournals.length === 0" slot="main-content-column" class="no-hover" :line1="'No journals found'"/>

        <div v-if="stats" slot="right-content-column">
            <h3>Insights</h3>
            <statistics-card :subject="'Needs marking'" :num="stats.needsMarking"/>
            <statistics-card :subject="'Unpublished grades'" :num="stats.unpublished"/>
            <statistics-card :subject="'Average points'" :num="stats.averagePoints"/>
        </div>
    </content-columns>
</template>

<script>
import contentColumns from '@/components/columns/ContentColumns.vue'
import studentCard from '@/components/assignment/StudentCard.vue'
import mainCard from '@/components/assets/MainCard.vue'
import statisticsCard from '@/components/assignment/StatisticsCard.vue'
import breadCrumb from '@/components/assets/BreadCrumb.vue'

import store from '@/Store.vue'
import assignmentAPI from '@/api/assignment'
import groupAPI from '@/api/group'
import participationAPI from '@/api/participation'
import icon from 'vue-awesome/components/Icon'

export default {
    name: 'Assignment',
    props: {
        cID: {
            required: true
        },
        aID: {
            required: true
        },
        jID: 0
    },
    data () {
        return {
            assignmentJournals: [],
            stats: [],
            groups: [],
            selectedSortOption: 'sortUsername',
            selectedFilterGroupOption: null,
            searchVariable: '',
            query: {},
            loadingJournals: true,
            order: false
        }
    },
    components: {
        'content-columns': contentColumns,
        'student-card': studentCard,
        'statistics-card': statisticsCard,
        'bread-crumb': breadCrumb,
        store,
        icon,
        'main-card': mainCard
    },
    created () {
        // TODO Should be moved to the breadcrumb, ensuring there is no more natural flow left that can get you to this
        // page without manipulating the url manually. If someone does this, simply let the error be thrown (no checks required)
        if (!this.$hasPermission('can_view_all_journals', 'assignment', String(this.aID))) {
            if (this.$root.previousPage) {
                this.$router.push({ name: this.$root.previousPage.name, params: this.$root.previousPage.params })
            } else {
                this.$router.push({ name: 'Home' })
            }
        }

        assignmentAPI.get(this.aID, this.cID)
            .then(assignment => {
                this.loadingJournals = false
                this.assignmentJournals = assignment.journals
            })

        if (this.$hasPermission('can_view_course_users')) {
            groupAPI.getAllFromCourse(this.cID)
                .then(groups => { this.groups = groups })
        }

        participationAPI.get(this.cID)
            .then(participant => {
                /* Group can be null */
                if (participant.group && participant.group.name) {
                    this.selectedFilterGroupOption = participant.group.name
                }
            })

        if (this.$route.query.sort === 'sortFullName' ||
            this.$route.query.sort === 'sortUsername' ||
            this.$route.query.sort === 'sortMarking') {
            this.selectedSortOption = this.$route.query.sort
        }

        if (this.$route.query.search) {
            this.searchVariable = this.$route.query.search
        }
    },
    methods: {
        handleEdit () {
            this.$router.push({
                name: 'FormatEdit',
                params: {
                    cID: this.cID,
                    aID: this.aID
                }
            })
        },
        publishGradesAssignment () {
            if (confirm('Are you sure you want to publish all grades for each journal?')) {
                assignmentAPI.update(this.aID, {published: true}, {
                    customErrorToast: 'Error while publishing all grades for this assignment.',
                    customSuccessToast: 'Published all grades for this assignment.'
                })
                    .then(_ => {
                        assignmentAPI.get(this.aID, this.cID)
                            .then(assignment => {
                                this.assignmentJournals = assignment.journals
                                this.stats = assignment.stats
                            })
                    })
            }
        },
        updateQuery () {
            if (this.searchVariable !== '') {
                this.query = {sort: this.selectedSortOption, search: this.searchVariable}
            } else {
                this.query = {sort: this.selectedSortOption}
            }

            if (this.$route.query !== this.query) {
                this.$router.replace({ query: this.query })
            }
        },
        compare (a, b) {
            if (a < b) { return this.order ? 1 : -1 }
            if (a > b) { return this.order ? -1 : 1 }
            return 0
        },
        toggleOrder () {
            this.order = !this.order
        },
        calcStats (filteredJournals) {
            var needsMarking = 0
            var unpublished = 0
            var points = 0

            for (var i = 0; i < filteredJournals.length; i++) {
                needsMarking += filteredJournals[i]['stats']['submitted'] - filteredJournals[i]['stats']['graded']
                unpublished += filteredJournals[i]['stats']['submitted'] - filteredJournals[i]['stats']['published']
                points += filteredJournals[i]['stats']['acquired_points']
            }
            this.stats['needsMarking'] = needsMarking
            this.stats['unpublished'] = unpublished - needsMarking
            this.stats['averagePoints'] = points / filteredJournals.length
        }
    },
    computed: {
        filteredJournals: function () {
            let self = this

            function compareFullName (a, b) {
                return self.compare(a.student.full_name, b.student.full_name)
            }

            function compareUsername (a, b) {
                return self.compare(a.student.username, b.student.username)
            }

            function compareMarkingNeeded (a, b) {
                return self.compare(a.stats.submitted - a.stats.graded, b.stats.submitted - b.stats.graded)
            }

            function searchFilter (assignment) {
                var username = assignment.student.username.toLowerCase()
                var fullName = assignment.student.full_name.toLowerCase()
                var searchVariable = self.searchVariable.toLowerCase()

                return username.includes(searchVariable) ||
                       fullName.includes(searchVariable)
            }

            function groupFilter (assignment) {
                if (self.selectedFilterGroupOption) {
                    return assignment.student.group === self.selectedFilterGroupOption
                }

                return true
            }

            /* Filter list based on search input. */
            if (this.selectedSortOption === 'sortFullName') {
                store.setFilteredJournals(this.assignmentJournals.filter(searchFilter).sort(compareFullName))
            } else if (this.selectedSortOption === 'sortUsername') {
                store.setFilteredJournals(this.assignmentJournals.filter(searchFilter).sort(compareUsername))
            } else if (this.selectedSortOption === 'sortMarking') {
                store.setFilteredJournals(this.assignmentJournals.filter(searchFilter).sort(compareMarkingNeeded))
            }

            this.updateQuery()
            this.calcStats(store.state.filteredJournals.filter(groupFilter))

            return store.state.filteredJournals.filter(groupFilter).slice()
        }
    }
}
</script>
