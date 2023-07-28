<?php
/**
 * Template for displaying lead info in pricing preview box.
 *
 * @author        ThemeMove
 * @package       Edumall/TutorLMS/Templates
 * @theme-since   2.4.0
 * @theme-version 2.4.0
 */

defined( 'ABSPATH' ) || exit;

global $edumall_course;
?>
<div class="tutor-single-course-meta tutor-meta-top">
	<?php
	do_action( 'edumall_course_single_enroll_box_lead_info_before' );
	?>

	<?php if ( '1' !== get_tutor_option( 'disable_course_level' ) ) { ?>
		<div class="tutor-course-level">
				<span class="meta-label">
					<i class="meta-icon far fa-sliders-h"></i>
					<?php esc_html_e( 'Level', 'edumall' ); ?>
				</span>
			<div class="meta-value"><?php echo get_tutor_course_level(); ?></div>
		</div>
	<?php } ?>

	<?php
	$disable_course_duration = get_tutor_option( 'disable_course_duration' );
	$course_duration         = Edumall_Tutor::instance()->get_course_duration_context();

	if ( ! empty( $course_duration ) && ! $disable_course_duration ) { ?>
		<div class="tutor-course-duration">
				<span class="meta-label">
					<i class="meta-icon far fa-clock"></i>
					<?php esc_html_e( 'Duration', 'edumall' ) ?>
				</span>
			<?php echo esc_html( $course_duration ); ?>
		</div>
	<?php } ?>

	<?php
	$tutor_lesson_count = $edumall_course->get_lesson_count();

	if ( $tutor_lesson_count ) : ?>
		<div class="tutor-course-lesson-count">
				<span class="meta-label">
					<i class="meta-icon far fa-play-circle"></i>
					<?php esc_html_e( 'Lectures', 'edumall' ); ?>
				</span>
			<div class="meta-value">
				<?php echo esc_html( sprintf( _n( '%s lecture', '%s lectures', $tutor_lesson_count, 'edumall' ), $tutor_lesson_count ) ); ?>
			</div>
		</div>
	<?php endif; ?>

	<?php Edumall_Tutor::instance()->entry_course_categories(); ?>

	<?php Edumall_Tutor::instance()->entry_course_language(); ?>

	<?php
	do_action( 'edumall_course_single_enroll_box_lead_info_after' );
	?>
</div>
