--
-- Name: account_audit; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.account_audit (
    id integer NOT NULL,
    account_subscription_id integer NOT NULL,
    date_started timestamp without time zone NOT NULL,
    date_updated timestamp without time zone NOT NULL,
    date_completed timestamp without time zone,
    active_criteria integer NOT NULL,
    criteria_processed integer NOT NULL,
    criteria_passed integer NOT NULL,
    criteria_failed integer NOT NULL,
    issues_found integer NOT NULL
);


ALTER TABLE public.account_audit OWNER TO cloud_sec_watch;

--
-- Name: account_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.account_audit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_audit_id_seq OWNER TO cloud_sec_watch;

--
-- Name: account_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.account_audit_id_seq OWNED BY public.account_audit.id;


--
-- Name: account_latest_audit; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.account_latest_audit (
    id integer NOT NULL,
    account_subscription_id integer NOT NULL,
    account_audit_id integer NOT NULL
);


ALTER TABLE public.account_latest_audit OWNER TO cloud_sec_watch;

--
-- Name: account_latest_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.account_latest_audit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_latest_audit_id_seq OWNER TO cloud_sec_watch;

--
-- Name: account_latest_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.account_latest_audit_id_seq OWNED BY public.account_latest_audit.id;


--
-- Name: account_subscription; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.account_subscription (
    id integer NOT NULL,
    account_id bigint NOT NULL,
    account_name character varying(255) NOT NULL,
    product_team_id integer NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE public.account_subscription OWNER TO cloud_sec_watch;

--
-- Name: account_subscription_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.account_subscription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_subscription_id_seq OWNER TO cloud_sec_watch;

--
-- Name: account_subscription_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.account_subscription_id_seq OWNED BY public.account_subscription.id;


--
-- Name: audit_criterion; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.audit_criterion (
    id integer NOT NULL,
    criterion_id integer NOT NULL,
    account_audit_id integer NOT NULL,
    regions integer NOT NULL,
    resources integer NOT NULL,
    tested integer NOT NULL,
    passed integer NOT NULL,
    failed integer NOT NULL,
    ignored integer NOT NULL
);


ALTER TABLE public.audit_criterion OWNER TO cloud_sec_watch;

--
-- Name: audit_criterion_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.audit_criterion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_criterion_id_seq OWNER TO cloud_sec_watch;

--
-- Name: audit_criterion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.audit_criterion_id_seq OWNED BY public.audit_criterion.id;


--
-- Name: audit_resource; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.audit_resource (
    id integer NOT NULL,
    criterion_id integer NOT NULL,
    account_audit_id integer NOT NULL,
    region character varying(255),
    resource_id character varying(255) NOT NULL,
    resource_name character varying(255),
    resource_data text NOT NULL,
    date_evaluated timestamp without time zone NOT NULL
);


ALTER TABLE public.audit_resource OWNER TO cloud_sec_watch;

--
-- Name: audit_resource_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.audit_resource_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_resource_id_seq OWNER TO cloud_sec_watch;

--
-- Name: audit_resource_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.audit_resource_id_seq OWNED BY public.audit_resource.id;


--
-- Name: criteria_provider; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.criteria_provider (
    id integer NOT NULL,
    provider_name character varying(255) NOT NULL
);


ALTER TABLE public.criteria_provider OWNER TO cloud_sec_watch;

--
-- Name: criteria_provider_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.criteria_provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.criteria_provider_id_seq OWNER TO cloud_sec_watch;

--
-- Name: criteria_provider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.criteria_provider_id_seq OWNED BY public.criteria_provider.id;


--
-- Name: criterion; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.criterion (
    id integer NOT NULL,
    criterion_name character varying(255) NOT NULL,
    criteria_provider_id integer NOT NULL,
    invoke_class_name character varying(255) NOT NULL,
    invoke_class_get_data_method character varying(255) NOT NULL,
    title text NOT NULL,
    description text NOT NULL,
    why_is_it_important text NOT NULL,
    how_do_i_fix_it text NOT NULL,
    active boolean NOT NULL,
    is_regional boolean NOT NULL
);


ALTER TABLE public.criterion OWNER TO cloud_sec_watch;

--
-- Name: criterion_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.criterion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.criterion_id_seq OWNER TO cloud_sec_watch;

--
-- Name: criterion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.criterion_id_seq OWNED BY public.criterion.id;


--
-- Name: criterion_params; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.criterion_params (
    id integer NOT NULL,
    criterion_id integer NOT NULL,
    param_name character varying(255) NOT NULL,
    param_value character varying(255) NOT NULL
);


ALTER TABLE public.criterion_params OWNER TO cloud_sec_watch;

--
-- Name: criterion_params_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.criterion_params_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.criterion_params_id_seq OWNER TO cloud_sec_watch;

--
-- Name: criterion_params_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.criterion_params_id_seq OWNED BY public.criterion_params.id;


--
-- Name: product_team; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.product_team (
    id integer NOT NULL,
    team_name character varying(255) NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE public.product_team OWNER TO cloud_sec_watch;

--
-- Name: product_team_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.product_team_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.product_team_id_seq OWNER TO cloud_sec_watch;

--
-- Name: product_team_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.product_team_id_seq OWNED BY public.product_team.id;


--
-- Name: product_team_user; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.product_team_user (
    id integer NOT NULL,
    user_id integer NOT NULL,
    team_id integer NOT NULL
);


ALTER TABLE public.product_team_user OWNER TO cloud_sec_watch;

--
-- Name: product_team_user_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.product_team_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.product_team_user_id_seq OWNER TO cloud_sec_watch;

--
-- Name: product_team_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.product_team_user_id_seq OWNED BY public.product_team_user.id;


--
-- Name: resource_compliance; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.resource_compliance (
    id integer NOT NULL,
    audit_resource_id integer NOT NULL,
    annotation text,
    resource_type character varying(255) NOT NULL,
    resource_id character varying(255) NOT NULL,
    compliance_type character varying(255) NOT NULL,
    is_compliant boolean NOT NULL,
    is_applicable boolean NOT NULL,
    status_id integer NOT NULL
);


ALTER TABLE public.resource_compliance OWNER TO cloud_sec_watch;

--
-- Name: resource_compliance_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.resource_compliance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.resource_compliance_id_seq OWNER TO cloud_sec_watch;

--
-- Name: resource_compliance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.resource_compliance_id_seq OWNED BY public.resource_compliance.id;


--
-- Name: resource_risk_assessment; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.resource_risk_assessment (
    id integer NOT NULL,
    criterion_id integer NOT NULL,
    audit_resource_id integer NOT NULL,
    account_audit_id integer NOT NULL,
    resource_id character varying(255) NOT NULL,
    date_first_identifed date NOT NULL,
    date_last_notified date,
    date_of_review date,
    accepted_risk boolean NOT NULL,
    analyst_assessed boolean NOT NULL,
    severity_id integer
);


ALTER TABLE public.resource_risk_assessment OWNER TO cloud_sec_watch;

--
-- Name: resource_risk_assessment_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.resource_risk_assessment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.resource_risk_assessment_id_seq OWNER TO cloud_sec_watch;

--
-- Name: resource_risk_assessment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.resource_risk_assessment_id_seq OWNED BY public.resource_risk_assessment.id;


--
-- Name: severity; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.severity (
    id integer NOT NULL,
    severity_name character varying(255) NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.severity OWNER TO cloud_sec_watch;

--
-- Name: severity_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.severity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.severity_id_seq OWNER TO cloud_sec_watch;

--
-- Name: severity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.severity_id_seq OWNED BY public.severity.id;


--
-- Name: status; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.status (
    id integer NOT NULL,
    status_name character varying(255) NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.status OWNER TO cloud_sec_watch;

--
-- Name: status_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.status_id_seq OWNER TO cloud_sec_watch;

--
-- Name: status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.status_id_seq OWNED BY public.status.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public."user" (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE public."user" OWNER TO cloud_sec_watch;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO cloud_sec_watch;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: user_session; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.user_session (
    id integer NOT NULL,
    date_opened timestamp without time zone NOT NULL,
    date_accessed timestamp without time zone NOT NULL,
    date_closed timestamp without time zone,
    user_id integer NOT NULL
);


ALTER TABLE public.user_session OWNER TO cloud_sec_watch;

--
-- Name: user_session_id_seq; Type: SEQUENCE; Schema: public; Owner: cloud_sec_watch
--

CREATE SEQUENCE IF NOT EXISTS public.user_session_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_session_id_seq OWNER TO cloud_sec_watch;

--
-- Name: user_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloud_sec_watch
--

ALTER SEQUENCE public.user_session_id_seq OWNED BY public.user_session.id;


--
-- Insert status data
--

INSERT INTO public.status (id, status_name, description)
VALUES
(1, 'Unknown', 'Not yet evaluated'),
(2, 'Pass', 'Compliant or not-applicable'),
(3, 'Fail', 'Non-compliant')
ON CONFLICT DO NOTHING;


--
-- Insert provider data
--

INSERT INTO public.criteria_provider (id, provider_name)
VALUES
(1, 'AWS Trusted Advisor'),
(2, 'AWS Elastic Cloud Compute (EC2) service'),
(3, 'AWS Identity and Access Management (IAM) service')
ON CONFLICT DO NOTHING;
