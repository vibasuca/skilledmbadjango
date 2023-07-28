<?php
/**
 * Template for displaying course content
 *
 * @since         v.1.6.7
 *
 * @author        Themeum
 * @url https://themeum.com
 *
 * @package       TutorLMS/Templates
 * @version       v.1.6.7
 *
 * @theme-since   2.4.0
 * @theme-version 2.8.5
 * @theme-deprecated 3.4.0
 */

defined( 'ABSPATH' ) || exit;

global $edumall_course;

$preview_box_classes = 'tutor-price-preview-box';

if ( '01' === Edumall::setting( 'single_course_layout' ) ) {
	if ( $edumall_course->has_video() || has_post_thumbnail() ) {
		$preview_box_classes .= ' box-has-media';
	}
}
?>

<div class="<?php echo esc_attr( $preview_box_classes ); ?>">
	<?php if ( '01' === Edumall::setting( 'single_course_layout' ) ) : ?>
		<div class="tutor-price-box-thumbnail">
			<?php
			if ( $edumall_course->has_video() ) {
				tutor_course_video();
			} else {
				Edumall_Image::the_post_thumbnail( [ 'size' => '340x200' ] );
			}
			?>
		</div>

		<?php do_action( 'tutor_course/single/enroll_box/after_thumbnail' ); ?>
	<?php endif; ?>

	<?php tutor_course_price(); ?>

	<?php tutor_load_template( 'single.course.custom.enroll-box-lead-info' ); ?>

	<?php tutor_course_material_includes_html(); ?>

	<div class="tutor-lead-info-btn-group">
		<?php do_action( 'tutor_course/single/actions_btn_group/before' ); ?>

		<?php tutor_load_template( 'single.course.custom.continue-lesson-button' ); ?>

		<?php tutor_load_template( 'custom.wishlist-button-01' ); ?>
	</div>

	<?php
	if ( tutor_utils()->get_option( 'enable_course_share', false, true, true ) ) {
		tutor_load_template( 'single.course.social_share' );
	}
	?>

</div> <!-- tutor-price-preview-box -->
