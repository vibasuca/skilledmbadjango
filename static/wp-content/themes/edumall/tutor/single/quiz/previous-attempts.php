<?php
/**
 * @package       TutorLMS/Templates
 * @version       1.6.4
 *
 * @theme-since   1.0.0
 * @theme-version 2.8.0
 */

defined( 'ABSPATH' ) || exit;

$previous_attempts = tutor_utils()->quiz_attempts();
$attempted_count   = is_array( $previous_attempts ) ? count( $previous_attempts ) : 0;
$attempts_allowed  = tutor_utils()->get_quiz_option( $quiz_id, 'attempts_allowed', 0 );
$attempt_remaining = (int) $attempts_allowed - (int) $attempted_count;
$passing_grade     = tutor_utils()->get_quiz_option( $quiz_id, 'passing_grade', 0 );
?>

<h4 class="tutor-quiz-attempt-history-title"><?php esc_html_e( 'Previous attempts', 'edumall' ); ?></h4>
<div class="tutor-quiz-attempt-history-table-wrap single-quiz-page dashboard-table-wrapper dashboard-table-responsive">
	<div class="dashboard-table-container">
		<table class="dashboard-table">
			<thead>
			<tr>
				<th class="col-attempt-number"><?php esc_html_e( '#', 'edumall' ); ?></th>
				<th><?php esc_html_e( 'Time', 'edumall' ); ?></th>
				<th><?php esc_html_e( 'Questions', 'edumall' ); ?></th>
				<th><?php esc_html_e( 'Total Marks', 'edumall' ); ?></th>
				<th><?php esc_html_e( 'Earned Marks', 'edumall' ); ?></th>
				<th><?php esc_html_e( 'Pass Mark', 'edumall' ); ?></th>
				<?php if ( class_exists( '\TUTOR_GB\GradeBook' ) ): ?>
					<th><?php esc_html_e( 'Grade', 'edumall' ); ?></th>
				<?php endif; ?>
				<th><?php esc_html_e( 'Result', 'edumall' ); ?></th>
				<?php do_action( 'tutor_quiz/previous_attempts/table/thead/col' ); ?>
			</tr>
			</thead>
			<tbody>
			<?php
			$loop_count = 0;
			?>
			<?php foreach ( $previous_attempts as $attempt ) : ?>
				<?php
				$loop_count++;
				?>
				<tr>
					<td class="col-attempt-number">
						<span class="attempt-number"><?php echo esc_html( $loop_count ); ?></span>
					</td>
					<td title="<?php esc_attr_e( 'Time', 'edumall' ); ?>">
						<div class="heading col-heading-mobile"><?php esc_html_e( 'Time', 'edumall' ); ?></div>
						<?php
						echo wp_date( get_option( 'date_format' ), strtotime( $attempt->attempt_started_at ) ) . ' ' . wp_date( get_option( 'time_format' ), strtotime( $attempt->attempt_started_at ) );

						if ( $attempt->is_manually_reviewed ) {
							?>
							<p class="attempt-reviewed-text">
								<?php
								echo __( 'Manually reviewed at', 'edumall' ) . wp_date( get_option( 'date_format', strtotime( $attempt->manually_reviewed_at ) ) ) . ' ' . wp_date( get_option( 'time_format', strtotime( $attempt->manually_reviewed_at ) ) );
								?>
							</p>
							<?php
						}
						?>
					</td>
					<td title="<?php esc_attr_e( 'Questions', 'edumall' ); ?>">
						<div class="heading col-heading-mobile"><?php esc_html_e( 'Questions', 'edumall' ); ?></div>
						<span class="attempt-questions"><?php echo esc_html( $attempt->total_questions ); ?></span>
					</td>

					<td title="<?php esc_attr_e( 'Total Marks', 'edumall' ); ?>">
						<div class="heading col-heading-mobile"><?php esc_html_e( 'Total Marks', 'edumall' ); ?></div>
						<span class="attempt-total-marks"><?php echo esc_html( $attempt->total_marks ); ?></span>
					</td>

					<td title="<?php esc_attr_e( 'Earned Marks', 'edumall' ); ?>">
						<div class="heading col-heading-mobile"><?php esc_html_e( 'Earned Marks', 'edumall' ); ?></div>
						<?php
						$earned_percentage = $attempt->earned_marks > 0 ? ( number_format( ( $attempt->earned_marks * 100 ) / $attempt->total_marks ) ) : 0;
						?>
						<span
							class="attempt-earned-marks"><?php echo esc_html( $attempt->earned_marks . "({$earned_percentage}%)" ); ?></span>
					</td>

					<td title="<?php esc_attr_e( 'Pass Mark', 'edumall' ); ?>">
						<div class="heading col-heading-mobile"><?php esc_html_e( 'Pass Mark', 'edumall' ); ?></div>
						<span class="attempt-pass-mark">
					<?php
					if ( $passing_grade > 0 ) {
						$pass_marks = ( $attempt->total_marks * $passing_grade ) / 100;
					} else {
						$pass_marks = 0;
					}
					if ( $pass_marks > 0 ) {
						echo number_format_i18n( $pass_marks, 2 );
					} else {
						echo 0;
					}
					if ( $passing_grade > 0 ) {
						echo "({$passing_grade}%)";
					} else {
						echo "(0%)";
					}
					?>
					</span>
					</td>

					<?php if ( class_exists( '\TUTOR_GB\GradeBook' ) ): ?>
						<td>
							<div class="heading col-heading-mobile"><?php esc_html_e( 'Grade', 'edumall' ); ?></div>
							<span class="attempt-grade">
							<?php
							$grade = get_gradebook_by_percent( $earned_percentage );
							echo tutor_generate_grade_html( $grade );
							?>
						</span>
						</td>
					<?php endif; ?>

					<td title="<?php esc_attr_e( 'Result', 'edumall' ); ?>">
						<div class="heading col-heading-mobile"><?php esc_html_e( 'Result', 'edumall' ); ?></div>
						<?php
						if ( $attempt->attempt_status === 'review_required' ) {
							echo '<span class="attempt-result attempt-result-review-required">' . esc_html__( 'Under Review', 'edumall' ) . '</span>';
						} else {
							if ( $earned_percentage >= $passing_grade ) {
								echo '<span class="attempt-result attempt-result-pass">' . esc_html__( 'Pass', 'edumall' ) . '</span>';
							} else {
								echo '<span class="attempt-result attempt-result-fail">' . esc_html__( 'Fail', 'edumall' ) . '</span>';
							}
						}
						?>
					</td>

					<?php do_action( 'tutor_quiz/previous_attempts/table/tbody/col', $attempt ); ?>
				</tr>
			<?php endforeach; ?>
			</tbody>
		</table>
	</div>
</div>
<?php
if ( $attempt_remaining > 0 || $attempts_allowed == 0 && $previous_attempts ) {
	do_action( 'tutor_quiz/start_form/before', $quiz_id );
	?>
	<div class="tutor-quiz-btn-grp tutor-mt-32">
		<form id="tutor-start-quiz" method="post">
			<?php wp_nonce_field( tutor()->nonce_action, tutor()->nonce ); ?>

			<input type="hidden" value="<?php echo esc_attr( $quiz_id ); ?>" name="quiz_id"/>
			<input type="hidden" value="tutor_start_quiz" name="tutor_action"/>

			<button type="submit" class="tutor-btn tutor-btn-primary tutor-btn-md start-quiz-btn" name="start_quiz_btn"
			        value="start_quiz">
				<?php esc_html_e( 'Start Quiz', 'edumall' ); ?>
			</button>
		</form>
	</div>
<?php } ?>
