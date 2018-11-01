<template>
    <journal-non-student v-if="$hasPermission('can_grade')" ref="journal-non-student-ref" :cID="cID" :aID="aID" :jID="jID"/>
    <journal-student v-else-if="$hasPermission('can_have_journal')" ref="journal-student-ref" :cID="cID" :aID="aID" :jID="jID"/>
</template>

<script>
import contentColumns from '@/components/columns/ContentColumns.vue'
import journalStudent from '@/components/journal/JournalStudent.vue'
import journalNonStudent from '@/components/journal/JournalNonStudent.vue'
import breadCrumb from '@/components/assets/BreadCrumb.vue'

export default {
    name: 'Journal',
    props: ['cID', 'aID', 'jID'],
    components: {
        'content-columns': contentColumns,
        'bread-crumb': breadCrumb,
        'journal-student': journalStudent,
        'journal-non-student': journalNonStudent
    },
    beforeRouteLeave (to, from, next) {
        if (this.$hasPermission('can_have_journal') && !this.$refs['journal-student-ref'].discardChanges()) {
            next(false)
            return
        }

        if (this.$hasPermission('can_grade') && !this.$refs['journal-non-student-ref'].discardChanges()) {
            next(false)
            return
        }

        next()
    }
}
</script>

<style lang="sass">
@import '~sass/partials/timeline-page-layout.sass'
</style>
