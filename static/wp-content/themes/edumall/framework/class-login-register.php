<?php
defined( 'ABSPATH' ) || exit;

if ( ! class_exists( 'Edumall_Login_Register' ) ) {

	class Edumall_Login_Register {

		/**
		 * Minimum Social Login, Social Sharing by miniOrange plugin version required.
		 *
		 * @since 2.6.0
		 *
		 * @var string
		 */
		const MINIMUM_MO_SOCIAL_LOGIN_VERSION = '7.4.7';

		protected static $instance = null;

		public static function instance() {
			if ( null === self::$instance ) {
				self::$instance = new self();
			}

			return self::$instance;
		}

		public function initialize() {
			add_filter( 'tutor_login_form_popup_html', [ $this, 'remove_tutor_popup_login' ] );

			add_action( 'wp_ajax_nopriv_edumall_user_login', [ $this, 'user_login' ] );

			add_action( 'wp_ajax_nopriv_edumall_user_register', [ $this, 'user_register' ] );

			add_action( 'wp_ajax_edumall_user_reset_password', [ $this, 'reset_password' ] );
			add_action( 'wp_ajax_nopriv_edumall_user_reset_password', [ $this, 'reset_password' ] );

			add_action( 'wp_enqueue_scripts', [ $this, 'login_scripts' ], 11 );

			add_action( 'wp_footer', [ $this, 'popup_login' ] );

			if ( defined( 'MO_OPENID_SOCIAL_LOGIN_VERSION' ) ) {
				add_action( 'edumall_after_popup_login_form', [ $this, 'add_social_login_buttons' ], 10 );

				/**
				 * @since 2.6.0
				 */
				if ( version_compare( MO_OPENID_SOCIAL_LOGIN_VERSION, self::MINIMUM_MO_SOCIAL_LOGIN_VERSION, '<' ) ) {
					add_action( 'admin_notices', [ $this, 'admin_notice_minimum_mo_social_login_version' ] );
				}
			}

			/**
			 * Fix Event Manager redirect.
			 */
			add_filter( 'logout_redirect', [ $this, 'logout_redirect' ], 99, 3 );
		}

		public function admin_notice_minimum_mo_social_login_version() {
			edumall_notice_required_plugin_version( 'Social Login, Social Sharing by miniOrange', self::MINIMUM_MO_SOCIAL_LOGIN_VERSION );
		}

		public function logout_redirect( $redirect_to, $requested_redirect_to, $use ) {
			return home_url();
		}

		public function login_scripts() {
			$min = Edumall_Enqueue::instance()->get_min_suffix();

			/**
			 * Disable unused scripts & styles from frontend of social login plugin.
			 */
			wp_dequeue_style( 'mo_openid_admin_settings_style' );
			wp_dequeue_style( 'mo_openid_admin_settings_phone_style' );
			wp_dequeue_style( 'mo-wp-bootstrap-social' );
			wp_dequeue_style( 'mo-wp-bootstrap-main' );
			wp_dequeue_style( 'mo-openid-sl-wp-font-awesome' );
			wp_dequeue_style( 'bootstrap_style_ass' );

			wp_dequeue_script( 'js-cookie-script' );
			// Don't need cache scroll position feature => don't enqueue again.
			wp_dequeue_script( 'mo-social-login-script' );

			wp_register_script( 'validate', EDUMALL_THEME_URI . '/assets/libs/validate/jquery.validate.min.js', [ 'jquery' ], '1.17.0', true );
			wp_register_script( 'edumall-login', EDUMALL_THEME_URI . "/assets/js/login{$min}.js", [
				'validate',
				'edumall-script',
			], '1.17.0', true );

			wp_enqueue_script( 'edumall-login' );

			/*
			 * Enqueue custom variable JS
			 */
			$js_variables = array(
				'validatorMessages' => [
					'required'    => esc_html__( 'This field is required', 'edumall' ),
					'remote'      => esc_html__( 'Please fix this field', 'edumall' ),
					'email'       => esc_html__( 'A valid email address is required', 'edumall' ),
					'url'         => esc_html__( 'Please enter a valid URL', 'edumall' ),
					'date'        => esc_html__( 'Please enter a valid date', 'edumall' ),
					'dateISO'     => esc_html__( 'Please enter a valid date (ISO)', 'edumall' ),
					'number'      => esc_html__( 'Please enter a valid number.', 'edumall' ),
					'digits'      => esc_html__( 'Please enter only digits.', 'edumall' ),
					'creditcard'  => esc_html__( 'Please enter a valid credit card number', 'edumall' ),
					'equalTo'     => esc_html__( 'Please enter the same value again', 'edumall' ),
					'accept'      => esc_html__( 'Please enter a value with a valid extension', 'edumall' ),
					'maxlength'   => esc_html__( 'Please enter no more than {0} characters', 'edumall' ),
					'minlength'   => esc_html__( 'Please enter at least {0} characters', 'edumall' ),
					'rangelength' => esc_html__( 'Please enter a value between {0} and {1} characters long', 'edumall' ),
					'range'       => esc_html__( 'Please enter a value between {0} and {1}', 'edumall' ),
					'max'         => esc_html__( 'Please enter a value less than or equal to {0}', 'edumall' ),
					'min'         => esc_html__( 'Please enter a value greater than or equal to {0}', 'edumall' ),
				],
			);
			wp_localize_script( 'edumall-login', '$edumallLogin', $js_variables );
		}

		public function popup_login() {
			if ( ! is_user_logged_in() ) {
				edumall_load_template( 'popup/popup-user' );
			}
		}

		public function user_login() {
			if ( ! check_ajax_referer( 'user_login', 'user_login_nonce' ) ) {
				wp_die();
			}

			/**
			 * Return array to prevent user login.
			 * For eg: array = [
			 *   'success'  => false,
			 *   'messages' => 'Some messages',
			 * ]
			 *
			 * @since 2.5.0
			 */
			$result = apply_filters( 'edumall_pre_user_login', null );

			if ( null !== $result ) {
				echo json_encode( $result );
				wp_die();
			}

			$user_login = $_POST['user_login'];
			$password   = $_POST['password'];
			$remember   = isset( $_POST['rememberme'] ) && 'forever' === $_POST['rememberme'] ? true : false;

			if ( filter_var( $user_login, FILTER_VALIDATE_EMAIL ) ) {
				$user = get_user_by( 'email', $user_login );
			} else {
				$user = get_user_by( 'login', $user_login );
			}

			$success = false;
			$msg     = esc_html__( 'Username or password is wrong. Please try again!', 'edumall' );

			if ( $user && wp_check_password( $password, $user->data->user_pass, $user->ID ) ) {
				$credentials = [
					'user_login'    => $user->data->user_login,
					'user_password' => $password,
					'remember'      => $remember,
				];

				$user = wp_signon( $credentials );

				if ( ! is_wp_error( $user ) ) {
					$success = true;
					$msg     = esc_html__( 'Login successful, Redirecting...', 'edumall' );
				}
			}

			$redirect_type = Edumall::setting( 'login_redirect' );
			$redirect_url  = '';

			switch ( $redirect_type ) {
				case 'home' :
					$redirect_url = home_url();
					break;
				case 'dashboard':
					if ( Edumall_Tutor::instance()->is_activated() ) {
						$redirect_url = tutor_utils()->get_tutor_dashboard_page_permalink();
					}
					break;
				case 'custom' :
					$redirect_url = Edumall::setting( 'custom_login_redirect' );
					break;
			}

			$redirect_url = apply_filters( 'edumall_login_redirect', $redirect_url );

			echo json_encode( [
				'success'      => $success,
				'messages'     => $msg,
				'redirect_url' => esc_url( $redirect_url ),
			] );

			wp_die();
		}

		public function user_register() {
			if ( ! check_ajax_referer( 'user_register', 'user_register_nonce' ) ) {
				wp_die();
			}

			/**
			 * Return array to prevent user register.
			 * For eg: array = [
			 *   'success'  => false,
			 *   'messages' => 'Some messages',
			 * ]
			 */
			$result = apply_filters( 'edumall_pre_user_register', null );

			if ( null !== $result ) {
				echo json_encode( $result );
				wp_die();
			}

			$firstname  = $_POST['firstname'];
			$lastname   = $_POST['lastname'];
			$email      = $_POST['email'];
			$password   = $_POST['password'];
			$user_login = $_POST['username'];
			$userdata   = [
				'first_name' => $firstname,
				'last_name'  => $lastname,
				'user_login' => $user_login,
				'user_email' => $email,
				'user_pass'  => $password,
			];

			// Remove all illegal characters from email.
			$email = filter_var( $email, FILTER_SANITIZE_EMAIL );

			$success = false;
			$msg     = esc_html__( 'Username/Email address is existing', 'edumall' );

			if ( ! filter_var( $email, FILTER_VALIDATE_EMAIL ) ) {
				$success = false;
				$msg     = esc_html__( 'A valid email address is required', 'edumall' );
			} else {
				$user_id = wp_insert_user( $userdata );

				if ( ! is_wp_error( $user_id ) ) {
					$creds                  = array();
					$creds['user_login']    = $user_login;
					$creds['user_email']    = $email;
					$creds['user_password'] = $password;
					$creds['remember']      = true;
					$user                   = wp_signon( $creds, false );

					$msg     = esc_html__( 'Congratulations, register successful, Redirecting...', 'edumall' );
					$success = true;

					do_action( 'edumall_user_register_after', $user_id );
				}

				echo json_encode( [
					'success'  => $success,
					'messages' => $msg,
				] );
			}

			wp_die();
		}

		public function reset_password() {
			if ( ! check_ajax_referer( 'user_reset_password', 'user_reset_password_nonce' ) ) {
				wp_die();
			}

			/**
			 * Return array to prevent user reset password.
			 * For eg: array = [
			 *   'success'  => false,
			 *   'messages' => 'Some messages',
			 * ]
			 *
			 * @since 2.5.0
			 */
			$result = apply_filters( 'edumall_pre_user_reset_password', null );

			if ( null !== $result ) {
				echo json_encode( $result );
				wp_die();
			}

			$allowed_html = array();
			$user_login   = wp_kses( $_POST['user_login'], $allowed_html );

			if ( empty( $user_login ) ) {
				echo json_encode( array(
					'success'  => false,
					'messages' => esc_html__( 'Enter a username or email address.', 'edumall' ),
				) );
				wp_die();
			}

			if ( filter_var( $user_login, FILTER_VALIDATE_EMAIL ) ) {
				$user_data = get_user_by( 'email', trim( $user_login ) );
				if ( empty( $user_data ) ) {
					echo json_encode( array(
						'success'  => false,
						'messages' => esc_html__( 'There is no user registered with that email address.', 'edumall' ),
					) );
					wp_die();
				}
			} else {
				$login     = trim( $user_login );
				$user_data = get_user_by( 'login', $login );

				if ( ! $user_data ) {
					echo json_encode( array(
						'success'  => false,
						'messages' => esc_html__( 'Invalid username', 'edumall' ),
					) );
					wp_die();
				}
			}

			$user_login = $user_data->user_login;
			$user_email = $user_data->user_email;
			$key        = get_password_reset_key( $user_data );

			if ( is_wp_error( $key ) ) {
				echo json_encode( array( 'success' => false, 'messages' => $key ) );
				wp_die();
			}

			$message = esc_html__( 'Someone has requested a password reset for the following account:', 'edumall' ) . "\r\n\r\n";
			$message .= network_home_url( '/' ) . "\r\n\r\n";
			$message .= sprintf( esc_html__( 'Username: %s', 'edumall' ), $user_login ) . "\r\n\r\n";
			$message .= esc_html__( 'If this was a mistake, just ignore this email and nothing will happen.', 'edumall' ) . "\r\n\r\n";
			$message .= esc_html__( 'To reset your password, visit the following address:', 'edumall' ) . "\r\n\r\n";
			$message .= '<' . network_site_url( "wp-login.php?action=rp&key=$key&login=" . rawurlencode( $user_login ), 'login' ) . ">\r\n";

			if ( is_multisite() ) {
				$blogname = $GLOBALS['current_site']->site_name;
			} else {
				$blogname = wp_specialchars_decode( get_option( 'blogname' ), ENT_QUOTES );
			}

			$title   = sprintf( esc_html__( '[%s] Password Reset', 'edumall' ), $blogname );
			$title   = apply_filters( 'retrieve_password_title', $title, $user_login, $user_data );
			$message = apply_filters( 'retrieve_password_message', $message, $key, $user_login, $user_data );
			if ( $message && ! wp_mail( $user_email, wp_specialchars_decode( $title ), $message ) ) {
				echo json_encode( array(
					'success'  => false,
					'messages' => esc_html__( 'The email could not be sent.', 'edumall' ) . "<br />\n" . esc_html__( 'Possible reason: your host may have disabled the mail function.', 'edumall' ),
				) );
				wp_die();
			} else {
				echo json_encode( array(
					'success'  => true,
					'messages' => esc_html__( 'Please, Check your email to get new password', 'edumall' ),
				) );
				wp_die();
			}
		}

		public function add_social_login_buttons() {
			echo do_shortcode( '[miniorange_social_login shape="longbuttonwithtext" view="horizontal" appcnt="2" space="0" theme="default" height="44" color="000000" heading="' . esc_html__( 'or Log-in with', 'edumall' ) . '"]' );
		}

		public function remove_tutor_popup_login( $html ) {
			return '';
		}
	}

	Edumall_Login_Register::instance()->initialize();
}
