<?php
/**
 * Template for displaying single lesson
 *
 * @author        Themeum
 * @url https://themeum.com
 * @package       TutorLMS/Templates
 * @since         v.1.0.0
 * @version       1.4.3
 *
 * @theme-since   1.0.0
 * @theme-version 3.0.0
 */

defined( 'ABSPATH' ) || exit;

get_tutor_header();

global $post;
$currentPost = $post;
?>
	<div class="page-content">

		<?php do_action( 'tutor_lesson/single/before/wrap' ); ?>

		<?php
		$enable_spotlight_mode = tutor_utils()->get_option( 'enable_spotlight_mode' );
		$wrapper_class         = 'tutor-single-lesson-wrap';

		if ( $enable_spotlight_mode ) {
			$wrapper_class .= ' tutor-spotlight-mode';
		}
		?>
		<div class="<?php echo esc_attr( $wrapper_class ); ?>">
			<div class="tutor-lesson-sidebar-wrap">
				<?php Edumall_Single_Lesson::instance()->lessons_sidebar(); ?>
			</div>
			<div id="tutor-single-entry-content"
			     class="tutor-lesson-content tutor-single-entry-content tutor-single-entry-content-<?php the_ID(); ?>">
				<div class="container">
					<?php tutor_lesson_content(); ?>
				</div>
			</div>
		</div>

		<?php do_action( 'tutor_lesson/single/after/wrap' ); ?>

	</div>
<?php
get_tutor_footer();
